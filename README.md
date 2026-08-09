# whereiszach.net

One question, one answer, one page.

## Changing the answer

Edit the `answer` field in [`answer.json`](answer.json). That is the whole system.
Every push to `main` rebuilds the page and deploys it, usually within a minute.

**From a phone or any browser:** open `answer.json` on GitHub, tap the pencil, change
the text between the quotes, commit.

**From this folder:**

```bash
./update.sh "Somewhere in Ohio"
```

## Ask Zach

The `ask zach` link at the bottom of the front page goes to `/ask.html`. Anyone can
ask — no account, no name, no email — and the question appears on the page straight
away. The feed filters by All / Answered / Unanswered.

### Answering

Add an `a` to the question in [`questions.json`](questions.json) and push. That is the
whole job.

```json
{
  "questions": [
    { "id": "qm3x1a2b", "q": "Best bar in Denver?", "a": "Williams & Graham.", "ts": 1786319000 }
  ]
}
```

Newest first. A question with no `a` still shows, marked *awaiting an answer*. Delete
an entry to remove it from the site.

### Where questions actually live

There is no server and no account anywhere in this, which takes one trick. The browser
posts the question straight into a [JSON Blob](https://jsonblob.com) — a public,
anonymous scratch space — and `harvest.py` copies anything it finds into
`questions.json`, which is the permanent record. Git is the source of truth; the blob
is only ever a 24-hour buffer.

Three consequences worth knowing:

- **Blobs expire exactly 24h after creation** and writing to one does not extend that.
  So the harvester rotates the inbox at the 12-hour mark and keeps draining the old
  blob until it lapses. `inbox.json` tracks the current blob and the ones still
  draining; the page fetches it fresh, so even a cached page finds a live inbox.
- **The blob is world-writable** — its URL is in the page source, which is exactly how
  anonymous posting works. Someone could wipe it. That costs at most 15 minutes of
  not-yet-harvested questions, and everything already in `questions.json` is in git.
- **Everything posts instantly, unmoderated.** A honeypot field, a 20-second cooldown,
  a 12-a-day cap and a 500-character limit blunt the obvious junk, but anything that
  gets through is live until you delete it from `questions.json`.

The deploy workflow runs the harvester before every build and on a 15-minute schedule,
committing new questions as it finds them.

## How it works

| File | Job |
| --- | --- |
| `answer.json` | The answer. The file you edit most. |
| `questions.json` | The permanent Ask Zach archive: questions and their answers. |
| `inbox.json` | Which blob the browser posts to right now. Maintained automatically. |
| `template.html` | The front page, with an `{{ANSWER}}` placeholder. |
| `ask.template.html` | The ask page: the form, the filter, and the live merge. |
| `build.py` | Fills the placeholders, writes `_site/`. Also owns the favicon. |
| `harvest.py` | Drains the inbox into `questions.json` and rotates the blob. |
| `CNAME` | Points GitHub Pages at the custom domain. |
| `.github/workflows/deploy.yml` | Harvests, builds and deploys — on push and every 15 min. |

Building at deploy time rather than fetching the answer in the browser means the
answer lands in the `<title>` and Open Graph tags, so link previews in Messages and
Slack show it too.

Preview locally:

```bash
python3 build.py && open _site/index.html
```

## DNS

`whereiszach.net` (apex) points at GitHub Pages:

```
A     @   185.199.108.153
A     @   185.199.109.153
A     @   185.199.110.153
A     @   185.199.111.153
CNAME www memyselfandzach.github.io
```
