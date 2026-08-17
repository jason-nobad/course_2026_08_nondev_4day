# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Course materials for **「AX 워크톤 부트캠프 — 비개발자 4일 오후 집중 과정」**, a Korean-language, 4-day afternoon bootcamp for non-developers run by 한국디지털문서플랫폼협회 · AcademiQ (2026-08-18 Tue → 08-21 Fri, 13:00–17:00 daily). It is **not a software project**: there is no build, lint, or test step, and no application code. The repo holds participant handouts (PDF), slide decks (PDF), and reference/example files (Markdown, HTML, DOCX, HWP).

All content is in Korean. Write new or edited material in Korean and reuse the course's own vocabulary (see below).

Participants **fork this repo** as their pair's team repository and commit all four days of deliverables into it. `README.md` is the participant-facing entry point (Korean): pre-course prep, fork instructions, day-by-day roadmap, the recommended output folders (`skills/`, `workflow/`, `docs/`, `tool/`, `_workspace/`, root `index.html`), a Day-4 package template section, and GitHub Pages steps. Keep README.md, `Docs/01_participant_guide.pdf`, and the slides consistent with each other when any of them changes.

## Working with the files

- **PDFs have no editable source here.** `Docs/*.pdf` are exports; the authoring files are not in the repo. Read them with `pdftotext -layout Docs/<file>.pdf -` (installed at `/opt/homebrew/bin/pdftotext`). Do not try to "edit" a PDF — if content must change, report what needs to change and where.
- **Editable files** are the `.md` and `.html` files in `References/`. `References/KSA0001_20230329.hwp` is Hangul Word Processor format and cannot be read with standard tools; the same standard is available as `.pdf`, `.docx`, and `.html` alongside it.
- Filenames in `Docs/` are numbered in the order participants encounter them (`01`–`03` pre-course handouts, `04`–`07` day-1…day-4 slides). Keep that scheme for any new handout.

## Layout and how the pieces relate

```
Docs/        participant-facing PDFs
  01_participant_guide   schedule, accounts to prepare (Cursor · Claude Pro+ · GitHub · ChatGPT), FAQ
  02_practice_topics     catalogue of 11 practice topics + "Best Practice 8가지"
  03_prelearning         pre-course self-study: AI principles, 스킬, 하네스
  04–07_slides_dayN      one deck per day (~42 pages each)
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

## Course concepts and vocabulary (use these terms consistently)

- **스킬** = "AI에게 주는 업무 매뉴얼" — a team-managed technical document, contrasted with a one-off 프롬프트.
- **하네스** = the five parts participants build over the four days: 스킬 · 금지 행동 · 폴더 규칙(`_workspace`: 원본/작업 중/최종) · 승인 게이트 · 검증 체크리스트.
- **바이브코딩** = 지시 → 생성 → 확인 → 수정 loop; **프롬프트 4요소** is the prompt structure taught on Day 2.
- Day → deliverable: Day 1 업무 문서 + 스킬 v0 (`skills/` folder in the team repo) → Day 2 안내 홈페이지 (`index.html`, merged via PR review) → Day 3 업무용 프로그램 built with Claude Code and verified against 샘플 3종 (정상·경계·오류) → Day 4 통합 파일럿 패키지 deployed on GitHub Pages (README 목차 + `index.html`).
- Guiding line: **"초안은 AI가, 확인과 책임은 사람이."** No 자동 발송 without human approval; 비식별 샘플 데이터 only (no real names, amounts, or confidential data) — apply this to any sample data you generate for the course too.

## Content conventions

- Every distributed document ends with the footer line
  `ⓒ 2026 한국디지털문서플랫폼협회 · AcademiQ(www.academiq.life) · 무단 복제·배포 금지 · …` — keep it on new materials.
- Dates, times, and the day-by-day deliverables above appear in several documents (guide, slides, `anchor_page.html`); if one changes, check the others for consistency.
- `design.md` and `anchor_page.html` deliberately borrow only design *principles* from orderful.com — do not copy its logo, trademarks, copy text, or customer logos into anything derived from them.
- `skills.md` is based on an unofficial excerpt of KS A 0001:2020; when it conflicts with the official text (e나라표준인증), the official text wins.
