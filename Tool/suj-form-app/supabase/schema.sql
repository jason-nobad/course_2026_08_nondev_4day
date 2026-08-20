-- suj-form-app: Supabase 스키마
-- 실행 방법: Supabase 대시보드 → SQL Editor → 새 쿼리 → 이 파일 전체 붙여넣고 Run
-- 데이터 계층(3-tier의 Data tier). 백엔드(Render)의 service_role 키만 이 테이블에 접근합니다.

create table if not exists public.complaints (
  id bigint generated always as identity primary key,
  receipt_no text unique not null,
  org text not null,
  contact_name text not null,
  contact_phone text not null,
  contact_email text,
  summary text not null,
  law text,
  detail text not null,
  direction text,
  has_evidence text not null check (has_evidence in ('있음', '없음')),
  urgent text not null check (urgent in ('일반', '긴급')),
  status text not null default '접수'
    check (status in ('접수', '검토중', '현황조사', '이사회보고', '기관협의', '완료', '반려')),
  created_at timestamptz not null default now()
);

create index if not exists complaints_receipt_no_idx on public.complaints (receipt_no);

-- 접수번호(EDPA-연도-번호) 채번용 연도별 카운터
create table if not exists public.complaint_seq (
  year int primary key,
  counter int not null default 0
);

-- 채번 + 등록을 한 트랜잭션으로 처리하는 함수 (동시 접수 시 번호 중복 방지)
create or replace function public.create_complaint(
  p_org text,
  p_contact_name text,
  p_contact_phone text,
  p_contact_email text,
  p_summary text,
  p_law text,
  p_detail text,
  p_direction text,
  p_has_evidence text,
  p_urgent text
) returns text
language plpgsql
security definer
set search_path = public
as $$
declare
  y int := extract(year from now());
  n int;
  receipt text;
begin
  insert into complaint_seq (year, counter) values (y, 1)
  on conflict (year) do update set counter = complaint_seq.counter + 1
  returning counter into n;

  receipt := 'EDPA-' || y || '-' || lpad(n::text, 4, '0');

  insert into complaints (
    receipt_no, org, contact_name, contact_phone, contact_email,
    summary, law, detail, direction, has_evidence, urgent
  ) values (
    receipt, p_org, p_contact_name, p_contact_phone, p_contact_email,
    p_summary, p_law, p_detail, p_direction, p_has_evidence, p_urgent
  );

  return receipt;
end;
$$;

-- RLS 활성화 + 정책 없음 = anon/authenticated 키로는 select/insert/update 전부 차단.
-- 백엔드는 service_role 키를 쓰므로 RLS를 우회해 정상 동작합니다(프런트가 DB에 직접 접근하지 않는 구조).
alter table public.complaints enable row level security;
alter table public.complaint_seq enable row level security;
