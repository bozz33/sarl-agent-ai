#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/CascadeProjects/SARL-agent-ai"
HBA_BACKUP="${1:-}"

[[ "$EUID" -eq 0 ]] || {
  echo "Run as root." >&2
  exit 1
}
[[ -f "$HBA_BACKUP" ]] || {
  echo "Usage: $0 /path/to/pg_hba.conf.backup" >&2
  exit 2
}

for profile in \
  sarl-router \
  sarl-orchestrator \
  sarl-orchestrator-critical \
  research-sage \
  docs-scribe; do
  docker exec -u hermes sarl-hermes-agent \
    /opt/hermes/.venv/bin/python - "$profile" <<'PY'
import sys
from pathlib import Path
import yaml
from utils import atomic_yaml_write

profile = sys.argv[1]
path = Path("/opt/data/profiles") / profile / "config.yaml"
config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
servers = config.get("mcp_servers")
if isinstance(servers, dict):
    servers.pop("sarl_project_memory", None)
    if not servers:
        config.pop("mcp_servers", None)
atomic_yaml_write(path, config, sort_keys=False)
PY
done

cd "$ROOT"
docker compose \
  -f docker-compose.yml \
  -f staging/stack-updates/docker-compose.project-memory.yml \
  stop project-memory-mcp
docker compose \
  -f docker-compose.yml \
  -f staging/stack-updates/docker-compose.project-memory.yml \
  rm -f project-memory-mcp

cp "$HBA_BACKUP" /etc/postgresql/16/main/pg_hba.conf
chown postgres:postgres /etc/postgresql/16/main/pg_hba.conf
chmod 640 /etc/postgresql/16/main/pg_hba.conf
sudo -u postgres psql -Atqc "select pg_reload_conf();"

echo "PROJECT_MEMORY_RUNTIME_ROLLBACK_OK"
