#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m book_blog_bot run \
  --pages "${BOOK_BOT_PAGES:-5}" \
  --count "${BOOK_BOT_COUNT:-5}" \
  --interval-seconds "${BOOK_BOT_INTERVAL_SECONDS:-300}" \
  "$@"
