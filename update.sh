#!/usr/bin/env bash
# Change the answer and publish it.
#   ./update.sh "Somewhere in Ohio"
set -euo pipefail

cd "$(dirname "$0")"

if [ $# -eq 0 ]; then
  echo 'Usage: ./update.sh "the new answer"' >&2
  exit 1
fi

ANSWER="$*"
python3 - "$ANSWER" <<'PY'
import json, sys, pathlib
pathlib.Path("answer.json").write_text(
    json.dumps({"answer": sys.argv[1]}, indent=2, ensure_ascii=False) + "\n"
)
PY

git add answer.json
git commit -m "Answer: $ANSWER"
git push

echo "Pushed. Live at https://whereiszach.net in about a minute."
