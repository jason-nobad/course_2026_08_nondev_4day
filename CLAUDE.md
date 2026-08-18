# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Course materials for **「AX 워크톤 부트캠프 — 비개발자 4일 오후 집중 과정」**, a Korean-language, 4-day afternoon bootcamp for non-developers run by 한국디지털문서플랫폼협회 · AcademiQ (2026-08-18 Tue → 08-21 Fri, 13:00–17:00 daily). It is **not a software project**: there is no build, lint, or test step, and no application code. The repo holds participant handouts (PDF), slide decks (PDF), and reference/example files (Markdown, HTML, DOCX, HWP).

All content is in Korean. Write new or edited material in Korean and reuse the course's own vocabulary (see below).

Participants **fork this repo** as their pair's team repository and commit all four days of deliverables into it. `README.md` is the participant-facing entry point (Korean): pre-course prep, fork instructions, day-by-day roadmap, the pre-created output folders (`Skills/`, `Workflow/`, `Outputs/`, `Tool/`, `_workspace/{01_input,02_working,03_final}/` — each with its own Korean README saying what goes there and when — plus root `index.html` made on Day 2), a Day-4 package template section, and GitHub Pages steps. Keep README.md, `materials/01_participant_guide.pdf`, and the slides consistent with each other when any of them changes.

## Working with the files

- **PDFs have no editable source here.** `materials/*.pdf` are exports; the authoring files are not in the repo. Read them with `pdftotext -layout materials/<file>.pdf -` (installed at `/opt/homebrew/bin/pdftotext`). Do not try to "edit" a PDF — if content must change, report what needs to change and where.
- **Slide decks also exist as HTML** in `docs/`: `dayN.html` (N=1–4) is the **presenter version** — one `.slide` div per 1280×720 page with base64-embedded images (~5–6 MB), plus the author's own presenter layer at the end of the file (`<style id="presenter">` + one `<script>`): one slide at a time scaled to the window, ←/→/Space/PgUp/PgDn/click navigation, `#N` in the URL, a per-slide time-budget timer (`BUD` array in seconds, one entry per slide — turns amber at 80 %, red/blinking when over; slides with a budget ≥ 600 s show remaining time), a wall clock, a progress bar, `F` fullscreen, `R` timer reset; `@media print` restores the stacked layout so browser-print yields the PDF. `slides_dayN.html` is the same deck **without** the presenter layer (print/plain). When editing slide content, keep the two in sync (the presenter file = plain file + presenter block). Preview with `python3 -m http.server <port>` → `/docs/day1.html`; on GitHub Pages the decks are at `…/docs/dayN.html` (lowercase — Pages is case-sensitive). Do not use `docs/` for learner output.
- **Editable files** are the `.md` and `.html` files in `References/`. `References/KSA0001_20230329.hwp` is Hangul Word Processor format and cannot be read with standard tools; the same standard is available as `.pdf`, `.docx`, and `.html` alongside it.
- Filenames in `materials/` are numbered in the order participants encounter them (`01`–`03` pre-course handouts, `04`–`07` day-1…day-4 slides). Keep that scheme for any new handout.
- Folder naming: `materials/` (PDF handouts) and `docs/` (slide HTML, lowercase so its Pages URL is `…/docs/…`) are lowercase; learner-output folders are capitalized (`Skills/`, `Workflow/`, `Outputs/`, `Tool/`) plus `References/`; `_workspace/` is lowercase because that is the course's own term. Learner outputs go in `Outputs/`, never in `docs/`. macOS/Windows are case-insensitive — never create a folder that differs from an existing one only by case (a `Docs/` would silently merge into `docs/`).

## Layout and how the pieces relate

```
materials/   participant-facing PDFs
  01_participant_guide   schedule, accounts to prepare (Cursor · Claude Pro+ · GitHub · ChatGPT), FAQ
  02_practice_topics     catalogue of 11 practice topics + "Best Practice 8가지"
  03_prelearning         pre-course self-study: AI principles, 스킬, 하네스
  04–07_slides_dayN      one deck per day (~42 pages each)
docs/        the same four decks as HTML — day1–4.html (presenter: navigation + per-slide budget timer) and slides_day1–4.html (plain/print)
References/  reference material and worked examples used in class
  skills.md              worked example of a "스킬" document (KS A 0001 standard-drafting rules)
  KSA0001_*              source documents behind skills.md — the same KS A 0001:2020 standard as
                         .pdf / .docx / .hwp, plus KSA0001_2020_standalone.{html,pdf} (재구성 발췌본)
  templateKS.docx        KS Draft Template referenced by skills.md
  design.md              worked example of a *design* 스킬 extracted from orderful.com (Day-2 homepage practice)
  orderful_info.md       background notes on the site analysed in design.md
  anchor_page.html       sample landing page for the course itself, built with the design.md system —
                         i.e. what a Day-2 "안내 홈페이지 → index.html" deliverable looks like
```

`skills.md` and `design.md` are the two canonical examples of the **skill-document format** the course teaches. New skill documents should follow the same shape:

1. YAML frontmatter with `name` and `description`
2. Numbered sections: 목적과 사용자 → 입력 → 작업 절차 → (domain-specific rules) → 완성 기준 (checklist) → 금지 행동 (each with a reason) → 버전과 변경 기록 (table, with a 개정 트리거)
3. A `> **근거/출처:**` blockquote near the top naming the source and its date

## The worked sample case (`sample_*` files)

Every output folder contains `sample_*` files that walk **one fictional case** end-to-end: ㈜가온물산 구매팀 (fictional mid-size manufacturer), practice topic 01 "주간 업무 보고 자동화", report week 2026-08-10 → 08-14, people 김가온 팀장(승인자) · 이하늘 대리(스킬 담당) · 박서준 사원 · 최유진 주임, suppliers 한빛부품 · 미래소재 · 누리패키징. The files reference each other by name and share the same items/dates, so **edit them together**: `Outputs/sample_00_priority` → `sample_01_weekly-report` → `Skills/sample_weekly-report` (+ glossary, prohibited) → `Workflow/sample_workflow` + `sample_raci` → `Tool/sample_weekly_report_tool.py` + `sample_USAGE` → `_workspace/01_input/sample_{normal,edge,error}` → `02_working/sample_…초안_v1` → `03_final/sample_…최종` → `Outputs/sample_checklist` → `sample_kpi` → `sample_brief`.

- The tool is real, stdlib-only Python 3. Verify it after any change with the three cases from the repo root:
  `python3 Tool/sample_weekly_report_tool.py sample_normal --date 2026-08-14` (writes a draft), `… sample_edge …` (writes with ⚠ review items), `… sample_error …` (must exit 1 and write nothing). It writes `_workspace/02_working/<date>_주간보고초안_v<n>.md`; delete those run artifacts afterwards — only the `sample_`-prefixed draft is meant to stay committed. `sample_2026-08-14_주간보고초안_v1.md` is the tool's actual `sample_normal` output plus one banner line; regenerate it if the tool's output format changes.
- Root `index.html` is the sample **Day-4 package cover** for the same case (deployable as-is via GitHub Pages: Settings → Pages → main / root). Single self-contained HTML (inline CSS/JS, no external assets). **Its design applies the tokens in `References/DESIGN_APPLE.md`** (despite the file name, that document is a consumer-marketplace design-system analysis): white canvas, ink `#222`, one accent `--primary #ff385c` used only for primary CTAs/orb/dot, hairlines `#ddd/#ebebeb`, type scale (display-xl 28/700 · display-md 21/700 · title-md 16/600 · body 16/14 · caption 14/500 · badge 11/600) with the single 64px "rating" moment on the hero KPI, radii 8/14/full, 4px spacing with 64px sections, exactly one shadow tier, and the system's component patterns (80px top nav with underline tabs, pill search bar + 48px orb, photo-first cards with plate/badge/32px icon button, 2-col detail with a sticky "reservation-style" request card that becomes a bottom bar under 744px, amenity rows, white footer + legal band). All tokens live as same-named CSS variables in `:root` — change the variable, not the rules. No logo/wordmark/copy of the analysed brand is used. Its "열기" links carry `data-repo="path"`; an inline script rewrites them to `https://github.com/<owner>/<repo>/blob/main/<path>` when served from `*.github.io` (relative otherwise) — keep that attribute on any new repo-file link. Numbers on the page (90분→20분, 3/3, 10항목, 4개, KPI table, 요청 3건, 비용) mirror `Outputs/sample_kpi.md` / `sample_brief.md`; update together. Preview with `python3 -m http.server <port>` from the repo root; to check the <744px layout, wrap it in a 400px `<iframe>` (window resize does not change the extension's screenshot viewport).
- Root `.nojekyll` (empty) disables Jekyll on GitHub Pages so `_workspace/` (underscore folder) and front-matter `.md` files are published untouched. Do not delete it.
- Every sample starts with a `> 📎 **샘플(가상 사례)**` banner and uses only dummy data (the "PII" in `sample_error/` is deliberately fake: `010-0000-0000`, `000000-0000000`). Keep it that way.

## Course concepts and vocabulary (use these terms consistently)

- **스킬** = "AI에게 주는 업무 매뉴얼" — a team-managed technical document, contrasted with a one-off 프롬프트.
- **하네스** = the five parts participants build over the four days: 스킬 · 금지 행동 · 폴더 규칙(`_workspace`: 원본/작업 중/최종) · 승인 게이트 · 검증 체크리스트.
- **바이브코딩** = 지시 → 생성 → 확인 → 수정 loop; **프롬프트 4요소** is the prompt structure taught on Day 2.
- Day → deliverable: Day 1 업무 문서 + 스킬 v0 (`Skills/` folder in the team repo) → Day 2 안내 홈페이지 (`index.html`, merged via PR review) → Day 3 업무용 프로그램 built with Claude Code and verified against 샘플 3종 (정상·경계·오류) → Day 4 통합 파일럿 패키지 deployed on GitHub Pages (README 목차 + `index.html`).
- Guiding line: **"초안은 AI가, 확인과 책임은 사람이."** No 자동 발송 without human approval; 비식별 샘플 데이터 only (no real names, amounts, or confidential data) — apply this to any sample data you generate for the course too.

## Content conventions

- Every distributed document ends with the footer line
  `ⓒ 2026 한국디지털문서플랫폼협회 · AcademiQ(www.academiq.life) · 무단 복제·배포 금지 · …` — keep it on new materials.
- Dates, times, and the day-by-day deliverables above appear in several documents (guide, slides, `anchor_page.html`); if one changes, check the others for consistency.
- `design.md` and `anchor_page.html` deliberately borrow only design *principles* from orderful.com — do not copy its logo, trademarks, copy text, or customer logos into anything derived from them.
- `skills.md` is based on an unofficial excerpt of KS A 0001:2020; when it conflicts with the official text (e나라표준인증), the official text wins.
