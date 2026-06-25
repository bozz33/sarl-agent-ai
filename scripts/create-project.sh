#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ID="${1:-}"
PROJECT_NAME="${2:-$PROJECT_ID}"

if [[ ! "$PROJECT_ID" =~ ^[a-z0-9][a-z0-9-]{1,62}$ ]]; then
  echo "Invalid project_id. Use lowercase letters, digits and hyphens." >&2
  exit 2
fi

PROJECT_ROOT="$ROOT/projects/$PROJECT_ID"

if [[ -e "$PROJECT_ROOT/project.yaml" ]]; then
  echo "Project already exists: $PROJECT_ROOT" >&2
  exit 1
fi

mkdir -p "$PROJECT_ROOT"/{source,documents,generated,reports,artifacts,worktrees,memory}

sed \
  -e "s/__PROJECT_ID__/$PROJECT_ID/g" \
  -e "s/__PROJECT_NAME__/$PROJECT_NAME/g" \
  "$ROOT/scripts/templates/project.yaml.template" \
  > "$PROJECT_ROOT/project.yaml"

sed \
  -e "s/__PROJECT_ID__/$PROJECT_ID/g" \
  -e "s/__PROJECT_NAME__/$PROJECT_NAME/g" \
  "$ROOT/scripts/templates/AGENTS.md.template" \
  > "$PROJECT_ROOT/AGENTS.md"

printf '# %s\n\nProjet inactif. Aucun worker automatique.\n' "$PROJECT_NAME" \
  > "$PROJECT_ROOT/README.md"

chown -R 10010:999 "$PROJECT_ROOT"
find "$PROJECT_ROOT" -type d -exec chmod 750 {} +
find "$PROJECT_ROOT" -type f -exec chmod 640 {} +

echo "$PROJECT_ROOT"
