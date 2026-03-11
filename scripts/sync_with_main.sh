#!/usr/bin/env bash
set -euo pipefail

REMOTE="${1:-origin}"
BASE_BRANCH="${2:-main}"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$CURRENT_BRANCH" == "$BASE_BRANCH" ]]; then
  echo "[error] Вы на базовой ветке '$BASE_BRANCH'. Переключитесь на рабочую ветку."
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "[error] Есть незакоммиченные изменения. Сначала закоммитьте или stash."
  exit 1
fi

echo "[info] Fetch: $REMOTE"
git fetch "$REMOTE"

echo "[info] Rebase '$CURRENT_BRANCH' on '$REMOTE/$BASE_BRANCH'"
git rebase "$REMOTE/$BASE_BRANCH"

echo "[info] Проверка конфликтных маркеров"
if rg -n "^(<<<<<<<|=======|>>>>>>>)" .; then
  echo "[error] Найдены конфликтные маркеры. Исправьте вручную и выполните:"
  echo "       git add <files> && git rebase --continue"
  exit 1
fi

echo "[info] Push with lease: $REMOTE $CURRENT_BRANCH"
git push --force-with-lease "$REMOTE" "$CURRENT_BRANCH"

echo "[ok] Ветка '$CURRENT_BRANCH' синхронизирована с '$REMOTE/$BASE_BRANCH'."
