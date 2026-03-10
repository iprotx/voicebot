#!/usr/bin/env bash
set -euo pipefail

NEW_REPO_URL="${1:-}"
TARGET_BRANCH="${2:-main}"
NEW_REMOTE_NAME="${3:-new-origin}"

if [[ -z "$NEW_REPO_URL" ]]; then
  echo "Usage: bash scripts/migrate_to_new_repo.sh <new_repo_url> [target_branch] [remote_name]"
  exit 1
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "[error] Current directory is not a git repository"
  exit 1
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "[error] There are uncommitted changes. Commit or stash before migration."
  exit 1
fi

if git remote get-url "$NEW_REMOTE_NAME" >/dev/null 2>&1; then
  git remote set-url "$NEW_REMOTE_NAME" "$NEW_REPO_URL"
  echo "[info] Updated remote '$NEW_REMOTE_NAME'"
else
  git remote add "$NEW_REMOTE_NAME" "$NEW_REPO_URL"
  echo "[info] Added remote '$NEW_REMOTE_NAME'"
fi

echo "[info] Pushing current branch '$CURRENT_BRANCH' -> '$NEW_REMOTE_NAME/$TARGET_BRANCH'"
git push -u "$NEW_REMOTE_NAME" "$CURRENT_BRANCH:$TARGET_BRANCH"

echo "[ok] Migration push completed"
echo "[next] Optional: make '$NEW_REMOTE_NAME' default"
echo "       git remote remove origin   # if present"
echo "       git remote rename $NEW_REMOTE_NAME origin"
