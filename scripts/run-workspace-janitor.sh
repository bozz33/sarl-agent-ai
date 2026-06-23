#!/usr/bin/env bash
set -euo pipefail

CONTAINER="sarl-hermes-workspace"
SCRIPT="/opt/sarl-maintenance/workspace-pty-janitor.py"

test "$(docker inspect "$CONTAINER" --format '{{.State.Health.Status}}')" = "healthy"
docker exec -u workspace "$CONTAINER" python3 "$SCRIPT"
