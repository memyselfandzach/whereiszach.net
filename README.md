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

The `ask zach` link at the bottom of the front page goes to `/ask.html`: a feed of
questions, and a button to ask a new one. Asking opens a GitHub issue — there is no
server here, so the issue tracker is the inbox. (That does mean asking requires a
GitHub account.)

Answering is the same move as changing the answer: edit
[`questions.json`](questions.json). Newest first.

```json
{
  "questions": [
    { "q": "Are you ever coming back to Chicago?", "a": "Sooner than you think." },
    { "q": "Best bar in Denver?" }
  ]
}
```

A question with no `a` still shows up on the page, marked *awaiting an answer*. Fill
in the `a` and it publishes. Close the matching issue when you have answered it.

## How it works

| File | Job |
| --- | --- |
| `answer.json` | The answer. The file you edit most. |
| `questions.json` | The Ask Zach feed: questions and their answers. |
| `template.html` | The front page, with an `{{ANSWER}}` placeholder. |
| `ask.template.html` | The ask page, with a `{{QUESTIONS}}` placeholder. |
| `build.py` | Fills the placeholders, writes `_site/`. Also owns the favicon. |
| `CNAME` | Points GitHub Pages at the custom domain. |
| `.github/workflows/deploy.yml` | Runs the build and deploys on every push to `main`. |

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
