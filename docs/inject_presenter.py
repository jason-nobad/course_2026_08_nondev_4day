#!/usr/bin/env python3
"""docs/day*.html 슬라이드에 발표 모드 블록(docs/presenter_snippet.html)을 주입/갱신한다.
슬라이드 HTML을 다시 생성해서 타이머·페이지 넘김이 사라졌을 때 저장소 루트에서 실행:
    python3 docs/inject_presenter.py            # day1~4 모두
    python3 docs/inject_presenter.py docs/day2.html
이미 들어 있으면 <!-- presenter:start --> ~ <!-- presenter:end --> 사이만 교체한다(여러 번 실행해도 안전).
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
snip = (HERE / "presenter_snippet.html").read_text(encoding="utf-8").strip("\n")
targets = [Path(a) for a in sys.argv[1:]] or sorted(HERE.glob("day*.html"))
for p in targets:
    s = p.read_text(encoding="utf-8")
    if "<!-- presenter:start" in s:
        s2 = re.sub(r"<!-- presenter:start.*?<!-- presenter:end -->", lambda m: snip, s, flags=re.S); how = "갱신"
    elif s.count("</body>") == 1:
        s2 = s.replace("</body>", snip + "\n</body>"); how = "삽입"
    else:
        print(f"건너뜀 {p}: </body>를 찾을 수 없음"); continue
    if s2 != s: p.write_text(s2, encoding="utf-8")
    print(f"{p.name}: {how}{'' if s2 != s else ' (변경 없음)'} · 슬라이드 {s2.count('class=\"slide')}장")
