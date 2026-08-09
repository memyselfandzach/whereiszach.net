#!/usr/bin/env python3
"""Render index.html from template.html + answer.json into _site/.

answer.json is the only file you ever need to edit.
"""

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"


def main() -> None:
    data = json.loads((ROOT / "answer.json").read_text())
    answer = str(data.get("answer", "")).strip() or "Unclear"

    page = (ROOT / "template.html").read_text()
    page = page.replace("{{ANSWER}}", html.escape(answer, quote=True))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "index.html").write_text(page)
    shutil.copy(ROOT / "CNAME", OUT / "CNAME")

    print(f'Built _site/index.html -> "{answer}"')


if __name__ == "__main__":
    main()
