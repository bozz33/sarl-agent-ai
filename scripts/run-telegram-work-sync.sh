#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="/run/lock/sarl-agent-ai-telegram-work-sync.lock"
CONTAINER="sarl-hermes-agent"
SCRIPT="/opt/sarl-maintenance/sync-telegram-work.py"
VALIDATION_SCRIPT="/opt/sarl-maintenance/apply-knowledge-validation.py"

exec 9>"$LOCK_FILE"
flock -n 9 || exit 0

test "$(docker inspect "$CONTAINER" --format '{{.State.Health.Status}}')" = "healthy"

docker exec -u hermes \
  -e HERMES_HOME=/opt/data \
  -e HERMES_KANBAN_BOARD=sarl-agent-ai \
  "$CONTAINER" \
  python "$SCRIPT" --ignore-message-id 866

# Apply human knowledge validations (valide:/rejette:<profil>) received over Telegram.
docker exec -u hermes \
  -e HERMES_HOME=/opt/data \
  "$CONTAINER" \
  python "$VALIDATION_SCRIPT"
