# Tool/ — 업무용 프로그램 (3일차)

3일차에 **Claude Code**로 만드는 업무 보조 도구와 그 사용법·검증 기록을 두는 폴더입니다.

## 언제 무엇을 넣나

| 날짜 | 넣는 것 |
|------|------|
| 3일 실습 1 | Claude Code가 만든 **프로그램 파일**(그대로 커밋) |
| 3일 실습 1 | **사용법** — 무엇을 넣으면 무엇이 나오는지, 실행 방법, 전제 조건 (아래 틀) |
| 3일 실습 2 | **샘플 3종 검증 기록** — 정상은 되는가 · 경계는 버티는가 · 오류는 멈추는가 |

## 사용법 문서 틀 (`USAGE.md`)

```markdown
# (도구 이름)

- 용도: 
- 입력: (파일 형식·위치 — `_workspace/01_input/`)
- 출력: (파일 형식·위치 — `_workspace/03_final/`)
- 실행 방법: (Claude Code에게 어떻게 말하면 되는지)
- 전제 조건·알려진 한계: 

## 검증 기록
| 샘플 | 기대 결과 | 실제 결과 | 통과/실패 | 날짜 |
|------|------|------|------|------|
| 정상 | | | | |
| 경계 | | | | |
| 오류 | 멈추고 "확인 필요" 표시 | | | |
```

## 유의 사항

- 도구는 **비식별 샘플**로만 시험합니다. 실데이터는 여기에도, `_workspace/`에도 올리지 않습니다.
- 비개발자의 유지보수 전략: ① 도구의 용도·전제를 스킬로 문서화 ② 샘플 3종 검증 기록 보관 ③ 고장 나면 Claude Code에게 검증 기록과 함께 다시 요청.

## 우리 팀 산출물

| 파일 | 무엇 |
|------|------|
| [`complaint_management_system.html`](complaint_management_system.html) | 전자문서산업계 애로사항·민원 통합관리 시스템 (`Downloads/prd.txt` PRD + `docs/prd_img/` 화면 목업 기반). 브라우저에서 더블클릭으로 실행되는 단일 HTML, 데이터는 localStorage에 저장 |
| [`complaint_management_system_USAGE.md`](complaint_management_system_USAGE.md) | 한 줄 명세 · 화면 구성표 · **샘플 3종 검증 기록(통과 33/33)** · 알려진 한계 · 버전 기록 |
| [`suj-form-app/`](suj-form-app/) | `docs/suj_form.html`(정적 mailto 양식)을 3-tier로 재구성한 접수 프로그램 — Vercel(프런트)·Render.com(백엔드 API)·Supabase(DB). 구조·배포 순서는 [`suj-form-app/README.md`](suj-form-app/README.md) 참고 |

## 샘플 (가상 사례: 주간 보고 초안 취합 도구)

| 파일 | 무엇 |
|------|------|
| [`sample_weekly_report_tool.py`](sample_weekly_report_tool.py) | 팀원 메모 → 주간 보고 초안 (파이썬 3, 외부 설치 없음). 스킬의 금지 행동을 코드로 옮김 |
| [`sample_USAGE.md`](sample_USAGE.md) | 한 줄 명세 · 실행 방법 · **샘플 3종 검증 기록(통과 3/3)** · 알려진 한계 · 버전 기록(v1→v1.1) |

직접 돌려 보기 (저장소 루트에서):

```bash
python3 Tool/sample_weekly_report_tool.py sample_normal --date 2026-08-14   # 초안 생성
python3 Tool/sample_weekly_report_tool.py sample_edge   --date 2026-08-14   # ⚠ 표시하며 생성
python3 Tool/sample_weekly_report_tool.py sample_error  --date 2026-08-14   # ⛔ 멈춤 (정상 동작)
```
