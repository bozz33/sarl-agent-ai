#!/usr/bin/env bash
set -euo pipefail

BACKUP="${1:-}"
[[ -n "$BACKUP" && -d "$BACKUP" ]] || {
  echo "Usage: $0 /absolute/path/to/backup" >&2
  exit 2
}

[[ -f "$BACKUP/SHA256SUMS" ]] || {
  echo "Missing SHA256SUMS" >&2
  exit 1
}

(cd "$BACKUP" && sha256sum -c SHA256SUMS)

TMP="$(mktemp -d /tmp/sarl-backup-verify.XXXXXX)"
cleanup() {
  rm -rf "$TMP"
}
trap cleanup EXIT

PROJECT_ARCHIVE=""
for candidate in \
  "$BACKUP/project/SARL-agent-ai-project.tar.gz" \
  "$BACKUP/project-files.tar.gz"; do
  if [[ -f "$candidate" ]]; then
    PROJECT_ARCHIVE="$candidate"
    break
  fi
done

[[ -n "$PROJECT_ARCHIVE" ]] || {
  echo "Missing project archive" >&2
  exit 1
}

mkdir -p "$TMP/project"
tar --no-same-owner -xzf "$PROJECT_ARCHIVE" -C "$TMP/project"

find "$TMP/project" -name docker-compose.yml -type f -print -quit \
  | grep -q docker-compose.yml

for archive in "$BACKUP"/volumes/*.tar.gz; do
  [[ -f "$archive" ]] || continue
  tar -tzf "$archive" >"$TMP/volume-archive-list.txt"
done

if [[ -f "$BACKUP/database/sarl_agent_memory.dump" ]]; then
  pg_restore --list "$BACKUP/database/sarl_agent_memory.dump" \
    >"$TMP/database-restore-list.txt"
fi

echo "BACKUP_RESTORE_VERIFY_OK"
