#!/usr/bin/env python3
"""Render the site into _site/.

Two files hold everything: answer.json is the status on the front page, and
questions.json is the Ask Zach feed. Fill in a question's "a" to publish the
answer.
"""

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"

# One stickman, defined once so every page shares the same tab icon.
FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 100 100'%3E"
    "%3Ccircle cx='50' cy='20' r='13' fill='black'/%3E"
    "%3Cg stroke='black' stroke-width='9' stroke-linecap='round' fill='none'%3E"
    "%3Cpath d='M50 33V66'/%3E%3Cpath d='M26 46H74'/%3E"
    "%3Cpath d='M50 66L30 92'/%3E%3Cpath d='M50 66L70 92'/%3E"
    "%3C/g%3E%3C/svg%3E"
)


def load(name: str) -> dict:
    """Read a JSON file, or fall back to empty so a typo can't break deploys."""
    path = ROOT / name
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def clean(items: list) -> list:
    """Only well-formed questions, newest first. The blob is world-writable."""
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        question = str(item.get("q", "")).strip()
        if not question:
            continue
        try:
            stamp = int(item.get("ts", 0))
        except (TypeError, ValueError):
            stamp = 0
        out.append({
            "id": str(item.get("id", "")).strip(),
            "q": question,
            "a": str(item.get("a") or "").strip(),
            "ts": stamp,
        })
    out.sort(key=lambda q: q["ts"], reverse=True)
    return out


def feed(items: list) -> str:
    """The Ask Zach list, rendered server-side so it works without JavaScript."""
    if not items:
        return '<p class="empty">No questions yet. Be the first.</p>'

    rows = []
    for item in items:
        answered = "true" if item["a"] else "false"
        body = (
            f'<p class="a">{html.escape(item["a"])}</p>' if item["a"]
            else '<p class="a waiting">awaiting an answer</p>'
        )
        ident = f' data-id="{html.escape(item["id"], quote=True)}"' if item["id"] else ""
        rows.append(
            f'<li data-answered="{answered}"{ident}>'
            f'<p class="q">{html.escape(item["q"])}</p>{body}</li>'
        )
    return '<ul class="feed" data-filter="all">' + "".join(rows) + "</ul>"


def render(template: str, **fields: str) -> str:
    page = (ROOT / template).read_text().replace("{{FAVICON}}", FAVICON)
    for name, value in fields.items():
        page = page.replace("{{" + name + "}}", value)
    return page


def main() -> None:
    answer = str(load("answer.json").get("answer", "")).strip() or "Unclear"
    questions = clean(load("questions.json").get("questions") or [])

    # The same list twice: as HTML for readers without JavaScript, and as JSON
    # for the script that merges in anything not yet harvested from the inbox.
    # </script> inside a question would otherwise close this block early.
    archive = json.dumps({"questions": questions}, ensure_ascii=False).replace("</", "<\\/")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "index.html").write_text(
        render("template.html", ANSWER=html.escape(answer, quote=True))
    )
    (OUT / "ask.html").write_text(
        render("ask.template.html", QUESTIONS=feed(questions), ARCHIVE_JSON=archive)
    )
    shutil.copy(ROOT / "CNAME", OUT / "CNAME")

    # The browser reads this to find today's inbox, so it ships with the site.
    inbox = ROOT / "inbox.json"
    if inbox.exists():
        shutil.copy(inbox, OUT / "inbox.json")

    waiting = sum(1 for q in questions if not q["a"])
    print(f'Built _site -> "{answer}"')
    print(f"  ask.html -> {len(questions)} question(s), {waiting} awaiting an answer")


if __name__ == "__main__":
    main()
