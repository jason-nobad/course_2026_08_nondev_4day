// suj-form-app: Application tier (Render.com 배포)
// 프런트(Vercel)와 데이터(Supabase) 사이의 유일한 통로.
// 프런트는 Supabase에 직접 접근하지 않고, 반드시 이 서버의 /api/* 를 거칩니다.

import express from "express";
import cors from "cors";
import rateLimit from "express-rate-limit";
import { createClient } from "@supabase/supabase-js";

const {
  SUPABASE_URL,
  SUPABASE_SERVICE_ROLE_KEY,
  ALLOWED_ORIGIN, // 쉼표로 여러 origin 지정 가능. 비워두면 모든 origin 허용(테스트용)
  ADMIN_KEY, // 내부 조회 페이지(/api/admin/*) 접근 키. 미설정 시 관리자 API 전체 비활성화
  PORT = 3000,
} = process.env;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  throw new Error(
    "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 환경변수가 설정되어 있지 않습니다. Render 대시보드 → Environment 에서 설정하세요."
  );
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { persistSession: false },
});

const app = express();
// Render는 리버스 프록시 뒤에서 실행되므로 X-Forwarded-For 헤더를 신뢰해야
// express-rate-limit이 접속자 IP를 정확히 구분합니다.
app.set("trust proxy", 1);
app.use(express.json({ limit: "200kb" }));

const allowedOrigins = (ALLOWED_ORIGIN || "")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);

app.use(
  cors({
    origin(origin, callback) {
      if (!origin || allowedOrigins.length === 0 || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error("허용되지 않은 origin입니다."));
      }
    },
  })
);

// 공개 폼이라 스팸 방지용 기본 속도 제한
app.use(
  "/api/",
  rateLimit({ windowMs: 15 * 60 * 1000, max: 30, standardHeaders: true, legacyHeaders: false })
);

const REQUIRED_FIELDS = [
  "org",
  "contact-name",
  "contact-phone",
  "summary",
  "detail",
  "has-evidence",
  "urgent",
];

function validate(body) {
  const errors = [];
  for (const field of REQUIRED_FIELDS) {
    if (!body[field] || typeof body[field] !== "string" || !body[field].trim()) {
      errors.push(`"${field}" 항목은 필수입니다.`);
    }
  }
  if (body["has-evidence"] && !["있음", "없음"].includes(body["has-evidence"])) {
    errors.push('"has-evidence" 값은 "있음" 또는 "없음"이어야 합니다.');
  }
  if (body["urgent"] && !["일반", "긴급"].includes(body["urgent"])) {
    errors.push('"urgent" 값은 "일반" 또는 "긴급"이어야 합니다.');
  }
  return errors;
}

app.post("/api/complaints", async (req, res) => {
  const body = req.body || {};
  const errors = validate(body);
  if (errors.length > 0) {
    return res.status(400).json({ ok: false, message: errors.join(" ") });
  }

  const { data, error } = await supabase.rpc("create_complaint", {
    p_org: body.org.trim(),
    p_contact_name: body["contact-name"].trim(),
    p_contact_phone: body["contact-phone"].trim(),
    p_contact_email: (body["contact-email"] || "").trim() || null,
    p_summary: body.summary.trim(),
    p_law: (body.law || "").trim() || null,
    p_detail: body.detail.trim(),
    p_direction: (body.direction || "").trim() || null,
    p_has_evidence: body["has-evidence"],
    p_urgent: body["urgent"],
  });

  if (error) {
    console.error("create_complaint 실패:", error);
    return res
      .status(500)
      .json({ ok: false, message: "접수 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요." });
  }

  return res.status(201).json({
    ok: true,
    receiptNo: data,
    message: "접수가 완료되었습니다.",
  });
});

// 접수번호 + 연락처가 모두 일치해야 조회 가능 (suj.md §6 처리 현황 확인)
app.get("/api/complaints/:receiptNo", async (req, res) => {
  const { receiptNo } = req.params;
  const phone = (req.query.phone || "").toString().trim();
  if (!phone) {
    return res.status(400).json({ ok: false, message: "조회하려면 접수 시 입력한 연락처가 필요합니다." });
  }

  const { data, error } = await supabase
    .from("complaints")
    .select("receipt_no, org, summary, status, urgent, created_at")
    .eq("receipt_no", receiptNo)
    .eq("contact_phone", phone)
    .maybeSingle();

  if (error) {
    console.error("조회 실패:", error);
    return res.status(500).json({ ok: false, message: "조회 중 오류가 발생했습니다." });
  }
  if (!data) {
    return res
      .status(404)
      .json({ ok: false, message: "접수번호와 연락처가 일치하는 건을 찾을 수 없습니다." });
  }
  return res.json({ ok: true, data });
});

// suj-form-app/supabase/schema.sql의 complaints.status check 제약과 반드시 일치시킬 것.
const STATUS_VALUES = ["접수", "검토중", "현황조사", "이사회보고", "기관협의", "완료", "반려"];

function requireAdminKey(req, res, next) {
  if (!ADMIN_KEY) {
    return res.status(503).json({ ok: false, message: "관리자 기능이 아직 설정되지 않았습니다." });
  }
  const key = req.header("x-admin-key") || "";
  if (key !== ADMIN_KEY) {
    return res.status(401).json({ ok: false, message: "접근 키가 올바르지 않습니다." });
  }
  next();
}

// 내부 접수 목록 조회 (간단한 관리 화면용). 공개 API가 아니므로 ADMIN_KEY로 최소 보호.
app.get("/api/admin/complaints", requireAdminKey, async (req, res) => {
  const { data, error } = await supabase
    .from("complaints")
    .select(
      "receipt_no, org, contact_name, contact_phone, contact_email, summary, law, detail, direction, has_evidence, urgent, status, created_at"
    )
    .order("created_at", { ascending: false })
    .limit(200);

  if (error) {
    console.error("접수 목록 조회 실패:", error);
    return res.status(500).json({ ok: false, message: "목록 조회 중 오류가 발생했습니다." });
  }
  return res.json({ ok: true, data });
});

// 접수 건 상태 변경 (간단한 관리 화면용).
app.patch("/api/admin/complaints/:receiptNo/status", requireAdminKey, async (req, res) => {
  const { receiptNo } = req.params;
  const status = (req.body && req.body.status) || "";

  if (!STATUS_VALUES.includes(status)) {
    return res.status(400).json({
      ok: false,
      message: `status 값은 다음 중 하나여야 합니다: ${STATUS_VALUES.join(", ")}`,
    });
  }

  const { data, error } = await supabase
    .from("complaints")
    .update({ status })
    .eq("receipt_no", receiptNo)
    .select("receipt_no, status")
    .maybeSingle();

  if (error) {
    console.error("상태 변경 실패:", error);
    return res.status(500).json({ ok: false, message: "상태 변경 중 오류가 발생했습니다." });
  }
  if (!data) {
    return res.status(404).json({ ok: false, message: "해당 접수번호를 찾을 수 없습니다." });
  }
  return res.json({ ok: true, data });
});

app.get("/health", (req, res) => res.json({ ok: true }));

app.listen(PORT, () => {
  console.log(`suj-form-backend listening on :${PORT}`);
});
