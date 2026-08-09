#!/usr/bin/env python3
"""Render index.html from template.html + answer.json into _site/.

answer.json is the only file you ever need to edit. The timestamp is derived
from the git commit that last touched it, so there is nothing else to keep
in sync.
"""

import html
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
TZ = ZoneInfo("America/Chicago")


def last_touched(path: str) -> datetime:
    """Commit time of the last change to `path`, or now if git can't say."""
    try:
        stamp = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", path],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if stamp:
            return datetime.fromisoformat(stamp).astimezone(TZ)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        pass
    return datetime.now(TZ)


def main() -> None:
    data = json.loads((ROOT / "answer.json").read_text())
    answer = str(data.get("answer", "")).strip() or "Unclear"

    updated = data.get("updated")
    if not updated:
        d = last_touched("answer.json")
        updated = f"{d:%B} {d.day}, {d:%Y}"

    page = (ROOT / "template.html").read_text()
    page = page.replace("{{ANSWER}}", html.escape(answer, quote=True))
    page = page.replace("{{UPDATED}}", html.escape(str(updated), quote=True))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "index.html").write_text(page)
    shutil.copy(ROOT / "CNAME", OUT / "CNAME")

    print(f'Built _site/index.html -> "{answer}" (as of {updated})')


if __name__ == "__main__":
    main()
