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

## How it works

| File | Job |
| --- | --- |
| `answer.json` | The answer. The only file you edit. |
| `template.html` | The page, with an `{{ANSWER}}` placeholder. |
| `build.py` | Fills the placeholder, writes `_site/index.html`. |
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
