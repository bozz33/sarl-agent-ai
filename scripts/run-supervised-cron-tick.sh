#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="/run/lock/sarl-agent-ai-cron-tick.lock"
HERMES="/opt/hermes/.venv/bin/hermes"
CONTAINER="sarl-hermes-agent"
ROOT="/root/CascadeProjects/SARL-agent-ai"

exec 9>"$LOCK_FILE"
flock -n 9 || exit 0

test "$(docker inspect "$CONTAINER" --format '{{.State.Health.Status}}')" = "healthy"

"$ROOT/scripts/collect-platform-health.sh"

for profile in \
  sarl-stack-steward \
  sarl-governor \
  designer-3d-agent \
  bureau-etudes-agent \
  community-manager; do
  docker exec -u hermes "$CONTAINER" \
    "$HERMES" -p "$profile" cron --accept-hooks tick
done
