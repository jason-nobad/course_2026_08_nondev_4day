# suj-form-app — 정책 애로사항 건의 접수 (3-tier)

`docs/suj_form.html`(정적 mailto 양식)을 실제 접수 이력이 서버에 남는 3계층(3-tier) 프로그램으로 재구성한 것입니다.
`docs/suj_form.html`은 그대로 두었습니다 (GitHub Pages로 배포되는 슬라이드 자료와 같은 폴더라 편집 대상이 아닙니다).
이 폴더가 실제로 배포·운영하는 버전입니다.

## 구조 (3-tier)

```mermaid
flowchart LR
    U[제출자 브라우저] -->|HTML/JS| FE[Presentation tier<br/>frontend/ · Vercel]
    FE -->|fetch /api/*| BE[Application tier<br/>backend/ · Render.com]
    BE -->|service_role 키| DB[(Data tier<br/>Supabase Postgres)]
```

| 계층 | 폴더 | 배포처 | 역할 |
|---|---|---|---|
| Presentation | [`frontend/`](frontend/) | Vercel (정적 사이트) | 접수 폼 + 접수번호 조회 화면. DB에 직접 접근하지 않고 백엔드 API만 호출 |
| Application | [`backend/`](backend/) | Render.com (Node 웹 서비스) | 입력값 검증, 접수번호(`EDPA-연도-번호`) 채번, Supabase 호출, 속도 제한 |
| Data | [`supabase/schema.sql`](supabase/schema.sql) | Supabase (Postgres) | `complaints` 테이블. RLS로 잠겨 있어 서비스 키를 가진 백엔드만 접근 가능 |

프런트가 Supabase에 직접 붙지 않고 반드시 백엔드를 거치도록 만든 것이 이 구조의 핵심입니다 — anon 키를 브라우저에 노출하지 않고, 검증·속도 제한·접수번호 채번 로직을 한 곳(Application tier)에 모을 수 있습니다.

## 배포 순서

### 1. Supabase (Data tier)

1. [supabase.com](https://supabase.com) 에서 새 프로젝트 생성
2. 대시보드 → **SQL Editor** → [`supabase/schema.sql`](supabase/schema.sql) 전체 붙여넣고 실행
3. **Project Settings → API** 에서 `Project URL`과 `service_role` 키를 복사해 둠 (service_role 키는 절대 프런트엔드나 공개 저장소에 넣지 않습니다)

### 2. Render.com (Application tier)

1. [render.com](https://render.com) → New → Web Service → 이 저장소 연결
2. Root Directory: `Tool/suj-form-app/backend` (또는 [`backend/render.yaml`](backend/render.yaml)을 Blueprint로 사용)
3. Environment 탭에서 환경변수 등록 ([`backend/.env.example`](backend/.env.example) 참고):
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `ALLOWED_ORIGIN` — 3단계에서 만들 Vercel 주소 (예: `https://suj-form.vercel.app`). 아직 모르면 임시로 비워두고, Vercel 배포 후 다시 채워 재배포
4. 배포 완료 후 `https://<서비스명>.onrender.com/health` 접속해 `{"ok":true}` 확인

### 3. Vercel (Presentation tier)

1. [`frontend/config.js`](frontend/config.js)의 `API_BASE_URL`을 2단계에서 받은 Render 주소로 수정 후 커밋
2. [vercel.com](https://vercel.com) → New Project → 이 저장소 연결, Root Directory를 `Tool/suj-form-app/frontend`로 지정 (빌드 명령 없음, 정적 파일 그대로 배포)
3. 배포된 주소를 Render의 `ALLOWED_ORIGIN`에 넣고 백엔드 재배포 (CORS 허용)

### 4. 동작 확인

- 배포된 Vercel 주소에서 폼 제출 → "접수번호: EDPA-2026-0001" 형태 메시지 확인
- Supabase 대시보드 → Table Editor → `complaints`에 행이 생겼는지 확인
- 같은 접수번호 + 연락처로 페이지 하단 "처리 현황 확인"에서 조회되는지 확인
- 필수 항목을 비운 채 제출 시 저장되지 않고 안내 메시지만 뜨는지 확인 (오류 샘플)

## 로컬에서 백엔드만 먼저 확인하고 싶다면

```bash
cd Tool/suj-form-app/backend
npm install
cp .env.example .env   # 값 채우기
npm start
curl -X POST http://localhost:3000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{"org":"테스트","contact-name":"홍길동","contact-phone":"010-0000-0000","summary":"테스트 접수","detail":"로컬 확인용","has-evidence":"없음","urgent":"일반"}'
```

## 알려진 한계

- 첨부파일 업로드는 아직 없습니다. 증빙 자료는 접수 후 담당자에게 별도로 전달하는 방식입니다 (필요해지면 Supabase Storage 연동으로 확장 가능).
- 접수 상태(`status`)는 기본값 `접수`로만 생성됩니다. 담당자가 검토·완료 등으로 바꾸는 관리 화면은 아직 없고, 현재는 Supabase 대시보드 → Table Editor에서 직접 수정합니다. `Tool/complaint_management_system.html`(localStorage 기반 내부 관리 도구)과 이 DB를 연동하는 것은 다음 단계 과제입니다.
- 관리자 인증은 없습니다(공개 접수 폼이므로 인증 불필요). 향후 담당자용 조회·상태변경 화면을 추가한다면 Supabase Auth로 로그인을 붙이는 것을 권장합니다.

## 버전과 변경 기록

| 버전 | 날짜 | 변경 내용 |
|---|---|---|
| v1.0 | 2026-08-20 | 최초 제작 — `docs/suj_form.html`(정적 mailto 양식)을 Vercel(프런트)·Render(백엔드)·Supabase(DB) 3-tier로 재구성. 접수번호 자동 채번, 접수번호+연락처 처리 현황 조회 추가 |
