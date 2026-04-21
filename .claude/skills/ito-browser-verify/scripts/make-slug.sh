#!/usr/bin/env bash
# 將驗證主題名稱轉為 slug，並附上當下時間戳，輸出檔名片段。
#
# Usage: make-slug.sh <topic>
# stdout: <slug>-<YYYYMMDD-HHMMSS>
# stderr: 錯誤訊息
# exit 0 成功，非 0 失敗。

set -u

if [ $# -ne 1 ]; then
  printf 'USAGE ERROR: make-slug.sh requires exactly one argument (topic).\n' >&2
  exit 1
fi

topic="$1"

if [ -z "$topic" ]; then
  printf 'INPUT ERROR: topic must not be empty.\n' >&2
  exit 1
fi

slug=$(printf '%s' "$topic" \
  | LC_ALL=C tr '[:upper:]' '[:lower:]' \
  | LC_ALL=C tr -c 'a-z0-9' '-' \
  | LC_ALL=C sed -E 's/-+/-/g; s/^-//; s/-$//')

if [ -z "$slug" ]; then
  slug="verify"
fi

timestamp=$(date +%Y%m%d-%H%M%S)

printf '%s-%s\n' "$slug" "$timestamp"
exit 0
