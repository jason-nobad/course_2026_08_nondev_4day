#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sample_weekly_report_tool.py — 주간 보고 초안 취합 도구 (샘플 · 가상 사례: ㈜가온물산 구매팀)

한 줄 명세:  팀원 업무 메모(memo_이름.md)들을 넣으면
           → 완료/진행/지연/다음 주/이슈로 취합하고, 지난주 보고와 비교해 변경점을 표시하고,
             지연 사유 누락·수치·미제출을 "검토 필요"로 표시해서
           → 팀장 승인 전 초안 파일(_workspace/02_working/YYYY-MM-DD_주간보고초안_v번호.md)이 나온다.

이 도구는 3일차 실습에서 Claude Code로 만드는 "업무용 프로그램"의 예시입니다.
- 외부 설치 없이 파이썬 3만 있으면 실행됩니다.
- 스킬(Skills/sample_weekly-report.md)의 규칙을 그대로 코드로 옮겼습니다.
  · 입력이 없거나 비면 지어내지 않고 멈춘다        (금지 6-1)
  · 지연 사유를 추정하지 않는다 — 없으면 "확인 필요"  (금지 6-2)
  · 금액·단가·%는 계산하지 않고 "[수치 원문 대조]"   (금지 6-3)
  · 개인정보 패턴이 보이면 즉시 중단               (금지 6-6)

사용법 (저장소 루트에서):
    python3 Tool/sample_weekly_report_tool.py sample_normal --date 2026-08-14
    python3 Tool/sample_weekly_report_tool.py sample_edge   --date 2026-08-14
    python3 Tool/sample_weekly_report_tool.py sample_error  --date 2026-08-14   # → 멈춰야 정상
옵션:
    케이스폴더      _workspace/01_input/ 아래 폴더 이름 (기본값 sample_normal)
    --date          보고 대상 주의 금요일 (기본값 오늘)
    --members       메모를 내야 하는 팀원 이름, 쉼표 구분 (기본값 이하늘,박서준,최유진)
"""

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

# ── 경로: 이 파일이 Tool/ 안에 있으므로, 부모의 부모가 저장소 루트 ───────────────────────
ROOT = Path(__file__).resolve().parent.parent
INPUT_ROOT = ROOT / "_workspace" / "01_input"
OUT_DIR = ROOT / "_workspace" / "02_working"

DEFAULT_MEMBERS = ["이하늘", "박서준", "최유진"]

# 메모의 절 제목 → 보고서 절 키
SECTION_KEYS = {
    "완료": "done", "진행": "doing", "지연": "late",
    "다음 주": "next", "다음주": "next", "이슈": "issue",
}
REPORT_TITLES = {
    "done": "① 이번 주 완료",
    "doing": "② 진행 중",
    "late": "③ 지연 (사유 포함)",
    "next": "④ 다음 주 계획",
    "issue": "⑤ 이슈·요청사항 (팀장 결정 필요 항목은 맨 위)",
}

# 비식별 위반 탐지 패턴 (보이면 즉시 중단)
PII_PATTERNS = {
    "휴대폰 번호": re.compile(r"01[016789]-?\d{3,4}-?\d{4}"),
    "주민등록번호 형식": re.compile(r"\b\d{6}-\d{7}\b"),
    "이메일 주소": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "카드번호 형식": re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b"),
}
# 수치(금액·단가·%) — 계산하지 않고 원문 대조 태그만 붙인다
# v1.1: 숫자가 있는 항목에만 태그 (v1에서 "견적 비교표 양식"처럼 숫자 없는 문구까지 태그되던 문제 수정)
NUMERIC_PATTERN = re.compile(r"\d[\d,.]*\s*(%|원)|(?=.*\d)(단가|금액|견적)")
MANY_ITEMS = 8  # 한 사람의 한 절에 이보다 많으면 "요약 검토" 경고


# ── 1. 읽기 ───────────────────────────────────────────────────────────────────────
def parse_sections(text: str) -> dict:
    """'## 절 제목' 아래의 '- 항목' 줄을 절별 목록으로 만든다. '없음'은 버린다."""
    sections = {k: [] for k in REPORT_TITLES}
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            title = line[3:].strip()
            current = next((v for k, v in SECTION_KEYS.items() if title.startswith(k)), None)
        elif line.startswith("- ") and current:
            item = line[2:].strip()
            if item and item != "없음":
                sections[current].append(item)
    return sections


def read_memos(case_dir: Path, members: list):
    """메모 파일을 읽고, 멈춰야 할 오류(errors)와 표시만 할 경고(warnings)를 모은다."""
    errors, warnings, memos = [], [], {}
    files = sorted(case_dir.glob("memo_*.md"))
    if not files:
        errors.append(f"메모 파일이 없습니다: {case_dir}")
        return memos, errors, warnings

    for f in files:
        name = f.stem.replace("memo_", "")
        text = f.read_text(encoding="utf-8")
        if not text.strip():
            errors.append(f"{name} 메모가 비어 있습니다 (0바이트) — 내용을 지어내지 않고 멈춥니다")
            continue
        for label, pat in PII_PATTERNS.items():
            if pat.search(text):
                errors.append(f"{name} 메모에 {label} 패턴이 있습니다 — 비식별 처리 후 다시 실행하세요")
        sections = parse_sections(text)
        if not any(sections.values()) and "## " not in text:
            errors.append(f"{name} 메모에서 절(## 완료/진행/지연/다음 주/이슈)을 찾지 못했습니다 — 형식 확인 필요")
        memos[name] = sections

    for m in members:
        if m not in memos:
            warnings.append(f"[미제출] {m} — 메모가 없습니다. 담당자에게 확인 요청")
    return memos, errors, warnings


def read_last_week() -> tuple:
    """지난주 승인본에서 '진행 중'·'지연' 항목을 뽑는다 (없으면 빈 목록)."""
    candidates = sorted(INPUT_ROOT.glob("*last_week_report_*.md"))
    if not candidates:
        return [], [], None
    text = candidates[-1].read_text(encoding="utf-8")
    doing, late, current = [], [], None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## ②"):
            current = doing
        elif line.startswith("## ③"):
            current = late
        elif line.startswith("## "):
            current = None
        elif line.startswith("- ") and current is not None:
            current.append(line[2:])
    return doing, late, candidates[-1].name


# ── 2. 비교·표시 ─────────────────────────────────────────────────────────────────
def norm(s: str) -> str:
    """문구 비교용 정규화: 괄호 안·'— 사유…'·공백·기호 제거."""
    s = re.sub(r"\(.*?\)", "", s)
    s = s.split("—")[0]
    return re.sub(r"[\s\W_]+", "", s).lower()


def matches(item: str, last_items: list) -> bool:
    n = norm(item)
    for l in last_items:
        nl = norm(l)
        if len(nl) >= 6 and (nl in n or n in nl):
            return True
    return False


# ── 3. 초안 만들기 ─────────────────────────────────────────────────────────────────
def build_report(memos, members, warnings, date: dt.date, last_doing, last_late, last_name):
    start = date - dt.timedelta(days=4)
    review = list(warnings)  # 검토 필요 항목 (미제출 등)
    lines = [
        f"# 구매팀 주간 업무 보고 ({start} ~ {date})",
        "",
        "> AI 초안 — 팀장 승인 전 · 대외 공유 금지",
        "",
        f"작성: 취합 도구(자동) · 작성일: {date} · 승인: — · 승인일: —",
    ]
    if last_name:
        lines.append(f"비교 기준: `{last_name}` (◀ 지난주 진행 → 완료 · ⚠ 2주 연속 지연)")
    lines.append("")

    for key in ["done", "doing", "late", "next", "issue"]:
        lines.append(f"## {REPORT_TITLES[key]}")
        rows = []
        for name in members + [m for m in memos if m not in members]:
            items = memos.get(name, {}).get(key, [])
            if len(items) > MANY_ITEMS:
                review.append(f"{name} '{REPORT_TITLES[key][2:].split(' (')[0]}' {len(items)}건 — 상위 보고 발췌 시 요약 검토")
            for it in items:
                row = f"- {it} ({name})"
                if key == "late":
                    if "사유" not in it:
                        row += " [확인 필요: 사유 없음]"
                        review.append(f"{name} 지연 항목 사유 없음: {it}")
                    if matches(it, last_late):
                        row += " ⚠ 2주 연속 지연"
                if key == "done" and matches(it, last_doing):
                    row += " ◀ 지난주 진행 → 완료"
                if re.search(r"\d", it) and NUMERIC_PATTERN.search(it):
                    row += " [수치 원문 대조]"
                    review.append(f"{name} 수치 포함 항목 원본 대조: {it}")
                rows.append(row)
        if key == "issue":  # 팀장 결정 필요 항목을 맨 위로
            rows.sort(key=lambda r: 0 if ("팀장" in r or "결정" in r or "판단" in r) else 1)
        lines += rows if rows else ["- (해당 없음)"]
        lines.append("")

    lines += ["---", "**검토 필요 항목**"]
    lines += [f"- {r}" for r in review] if review else ["- 없음"]
    lines += ["", "<sub>본 문서는 도구가 만든 초안입니다. 팀장 승인 전에는 대외 공유하지 않습니다.</sub>", ""]
    return "\n".join(lines), review


def next_version_path(date: dt.date) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n = len(list(OUT_DIR.glob(f"{date}_주간보고초안_v*.md"))) + 1
    return OUT_DIR / f"{date}_주간보고초안_v{n}.md"


# ── 4. 실행 ────────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="주간 보고 초안 취합 도구 (샘플)")
    ap.add_argument("case", nargs="?", default="sample_normal", help="_workspace/01_input/ 아래 케이스 폴더")
    ap.add_argument("--date", default=dt.date.today().isoformat(), help="보고 대상 주의 금요일 YYYY-MM-DD")
    ap.add_argument("--members", default=",".join(DEFAULT_MEMBERS), help="메모 제출 대상 팀원 (쉼표 구분)")
    args = ap.parse_args()

    date = dt.date.fromisoformat(args.date)
    members = [m.strip() for m in args.members.split(",") if m.strip()]
    case_dir = INPUT_ROOT / args.case
    if not case_dir.is_dir():
        print(f"⛔ 중단 — 입력 폴더가 없습니다: {case_dir}")
        return 1

    memos, errors, warnings = read_memos(case_dir, members)
    if errors:
        print("⛔ 중단 — 초안을 만들지 않았습니다. 이유:")
        for e in errors:
            print(f"   · {e}")
        print("   → 입력을 고친 뒤 다시 실행하세요. (스킬 금지 행동 6-1 · 6-6)")
        return 1

    last_doing, last_late, last_name = read_last_week()
    report, review = build_report(memos, members, warnings, date, last_doing, last_late, last_name)
    out = next_version_path(date)
    out.write_text(report, encoding="utf-8")

    print(f"✅ 초안 생성: {out.relative_to(ROOT)}")
    print(f"   입력: {case_dir.relative_to(ROOT)} (메모 {len(memos)}건) · 비교: {last_name or '없음'}")
    if review:
        print(f"⚠ 검토 필요 항목 {len(review)}건 — 초안 하단 참조:")
        for r in review:
            print(f"   · {r}")
    else:
        print("   검토 필요 항목 없음")
    print("   다음 단계: 담당자 검토 → 팀장 승인 → _workspace/03_final/ 로 이동")
    return 0


if __name__ == "__main__":
    sys.exit(main())
