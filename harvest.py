#!/usr/bin/env python3
"""Drain the public question inbox into questions.json.

Questions are submitted straight from the browser to a JSON Blob, which needs
no account from the asker and no server from us. Blobs die exactly 24h after
they are created -- writing to one does not extend that -- so this script also
rotates the inbox well before expiry and keeps draining the outgoing blob until
it lapses. Anything harvested here is committed to git, which is the permanent
record; the blob is only ever a buffer.

Run by the deploy workflow before every build.
"""

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
INBOX = ROOT / "inbox.json"
ARCHIVE = ROOT / "questions.json"

API = "https://jsonblob.com/api/jsonBlob"
DAY = 24 * 60 * 60
ROTATE_AFTER = 12 * 60 * 60   # rotate at half-life, so a stale page still lands
KEEP_DRAINING = DAY + 3600    # keep reading an old blob until it is truly gone

MAX_LEN = 500                 # a question, not an essay
MIN_LEN = 3
MAX_PER_RUN = 200             # a spam flood can't blow up the archive in one go
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def http(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.status, res.headers, res.read().decode()


def read_json(name, fallback):
    path = ROOT / name
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return fallback


def clean(text):
    """Whatever the internet posted, reduced to a single tidy line or None."""
    text = CONTROL.sub("", str(text)).strip()
    text = re.sub(r"\s+", " ", text)
    if not (MIN_LEN <= len(text) <= MAX_LEN):
        return None
    return text


def drain(url):
    """Every usable question sitting in one blob. Never raises."""
    try:
        _, _, raw = http("GET", url)
        payload = json.loads(raw)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError,
            TimeoutError, OSError):
        return []

    items = payload.get("questions") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return []

    out = []
    for item in items[:MAX_PER_RUN]:
        if not isinstance(item, dict):
            continue
        question = clean(item.get("q", ""))
        if not question:
            continue
        ident = str(item.get("id", "")).strip()[:64]
        try:
            stamp = int(item.get("ts", 0))
        except (TypeError, ValueError):
            stamp = 0
        out.append({
            "id": ident or f"q{stamp}_{abs(hash(question)) % 10**8}",
            "q": question,
            "ts": stamp or int(time.time()),
        })
    return out


def create_blob():
    _, headers, _ = http("POST", API, {"questions": []})
    location = headers.get("Location", "")
    if not location:
        raise RuntimeError("jsonblob did not return a Location for the new blob")
    if location.startswith("http"):
        return location
    return "https://jsonblob.com" + location


def main():
    now = int(time.time())
    inbox = read_json("inbox.json", {})
    current = inbox.get("current") or {}
    draining = [d for d in inbox.get("draining", []) if isinstance(d, dict)]

    # 1. Pull everything out of the live blob and any still-breathing old ones.
    sources = [current] + draining
    harvested = []
    for source in sources:
        url = str(source.get("url", ""))
        if url.startswith("https://jsonblob.com/"):
            harvested.extend(drain(url))

    # 2. Fold what is new into the archive. Git is the source of truth.
    archive = read_json("questions.json", {"questions": []})
    questions = archive.get("questions")
    if not isinstance(questions, list):
        questions = []

    seen = {str(q.get("id")) for q in questions if isinstance(q, dict) and q.get("id")}
    fresh = []
    for item in harvested:
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        fresh.append(item)

    if fresh:
        fresh.sort(key=lambda q: q["ts"], reverse=True)
        questions = fresh + questions

    # 3. Rotate the inbox before it can expire under a visitor's feet.
    rotated = False
    born = int(current.get("created", 0) or 0)
    if not current.get("url") or (now - born) > ROTATE_AFTER:
        try:
            url = create_blob()
        except Exception as exc:                      # noqa: BLE001 - never fail the build
            print(f"could not rotate the inbox ({exc}); keeping the current one")
        else:
            if current.get("url"):
                draining.append(current)
            current = {"url": url, "created": now}
            rotated = True

    draining = [
        d for d in draining
        if d.get("url") != current.get("url")
        and (now - int(d.get("created", 0) or 0)) < KEEP_DRAINING
    ]

    changed = bool(fresh) or rotated
    if changed:
        ARCHIVE.write_text(
            json.dumps({"questions": questions}, indent=2, ensure_ascii=False) + "\n"
        )
        INBOX.write_text(
            json.dumps({"current": current, "draining": draining}, indent=2) + "\n"
        )

    unanswered = sum(
        1 for q in questions
        if isinstance(q, dict) and not str(q.get("a") or "").strip()
    )
    print(f"harvested {len(fresh)} new question(s); "
          f"{len(questions)} archived, {unanswered} unanswered; "
          f"inbox {'rotated' if rotated else 'unchanged'}, "
          f"{len(draining)} draining")

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"changed={'true' if changed else 'false'}\n")


if __name__ == "__main__":
    main()
