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


def feed(items: list) -> str:
    """The Ask Zach list. Unanswered questions are shown, just quietly."""
    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue
        question = str(item.get("q", "")).strip()
        if not question:
            continue
        answer = str(item.get("a") or "").strip()
        body = (
            f'<p class="a">{html.escape(answer)}</p>' if answer
            else '<p class="a pending">awaiting an answer</p>'
        )
        rows.append(f'<li><p class="q">{html.escape(question)}</p>{body}</li>')

    if not rows:
        return '<p class="pending">No questions yet.</p>'
    return '<ul class="feed">' + "".join(rows) + "</ul>"


def render(template: str, **fields: str) -> str:
    page = (ROOT / template).read_text().replace("{{FAVICON}}", FAVICON)
    for name, value in fields.items():
        page = page.replace("{{" + name + "}}", value)
    return page


def main() -> None:
    answer = str(load("answer.json").get("answer", "")).strip() or "Unclear"
    questions = load("questions.json").get("questions") or []

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "index.html").write_text(
        render("template.html", ANSWER=html.escape(answer, quote=True))
    )
    (OUT / "ask.html").write_text(
        render("ask.template.html", QUESTIONS=feed(questions))
    )
    shutil.copy(ROOT / "CNAME", OUT / "CNAME")

    waiting = sum(1 for q in questions if not str(q.get("a") or "").strip())
    print(f'Built _site -> "{answer}"')
    print(f"  ask.html -> {len(questions)} question(s), {waiting} awaiting an answer")


if __name__ == "__main__":
    main()
