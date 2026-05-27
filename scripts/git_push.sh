#!/usr/bin/env bash
set -euo pipefail

POST_PATH="${1:-}"

if [[ -z "$POST_PATH" ]]; then
  echo "Usage: scripts/git_push.sh <hugo-post-path>" >&2
  exit 64
fi

if ! REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  echo "현재 폴더가 git 저장소가 아닙니다. 먼저 git init 및 GitHub remote를 설정하세요." >&2
  exit 1
fi

cd "$REPO_ROOT"

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "origin remote가 없습니다. 예: git remote add origin git@github.com:<USER>/<REPO>.git" >&2
  exit 1
fi

git add "$POST_PATH"

if git diff --cached --quiet; then
  echo "커밋할 변경사항이 없습니다: $POST_PATH"
  exit 0
fi

POST_NAME="$(basename "$POST_PATH" .md)"
git commit -m "Add crawled book post: ${POST_NAME}"

BRANCH="${BOOK_BOT_BRANCH:-$(git branch --show-current)}"
if [[ -z "$BRANCH" ]]; then
  BRANCH="main"
fi

git push origin "$BRANCH"
