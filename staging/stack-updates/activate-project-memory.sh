#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/CascadeProjects/SARL-agent-ai"
HBA="/etc/postgresql/16/main/pg_hba.conf"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
HBA_BACKUP="$ROOT/backups/postgres/pg_hba.conf.$STAMP"
RULE="local   sarl_agent_memory   sarl_memory_user   scram-sha-256"

[[ "$EUID" -eq 0 ]] || {
  echo "Run as root." >&2
  exit 1
}

cp "$HBA" "$HBA_BACKUP"
chmod 600 "$HBA_BACKUP"

if ! grep -Fqx "$RULE" "$HBA"; then
  TMP="$(mktemp)"
  awk -v rule="$RULE" '
    !inserted && $1 == "local" && $2 == "all" && $3 == "all" {
      print rule
      inserted=1
    }
    { print }
    END {
      if (!inserted) print rule
    }
  ' "$HBA" > "$TMP"
  chown postgres:postgres "$TMP"
  chmod 640 "$TMP"
  mv "$TMP" "$HBA"
fi

sudo -u postgres psql -Atqc "select pg_reload_conf();"

cd "$ROOT"
docker compose \
  -f docker-compose.yml \
  -f staging/stack-updates/docker-compose.project-memory.yml \
  up -d project-memory-mcp

for _ in $(seq 1 30); do
  if docker inspect sarl-project-memory-mcp \
    --format '{{.State.Health.Status}}' 2>/dev/null | grep -qx healthy; then
    break
  fi
  sleep 2
done

docker inspect sarl-project-memory-mcp \
  --format '{{.State.Health.Status}}' | grep -qx healthy

for profile in \
  sarl-router \
  sarl-orchestrator \
  sarl-orchestrator-critical \
  research-sage \
  docs-scribe; do
  docker exec -u hermes sarl-hermes-agent \
    /opt/hermes/.venv/bin/hermes -p "$profile" \
    config set mcp_servers.sarl_project_memory.url \
    http://project-memory-mcp:8000/mcp
  docker exec -u hermes sarl-hermes-agent \
    /opt/hermes/.venv/bin/hermes -p "$profile" \
    config set mcp_servers.sarl_project_memory.enabled true
  docker exec -u hermes sarl-hermes-agent \
    /opt/hermes/.venv/bin/hermes -p "$profile" \
    mcp test sarl_project_memory >/dev/null
done

echo "PROJECT_MEMORY_ACTIVATION_OK"
echo "HBA_BACKUP=$HBA_BACKUP"
