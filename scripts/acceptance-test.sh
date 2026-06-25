#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES="/opt/hermes/.venv/bin/hermes"
ACTIVE_PROFILES=(
  sarl-router
  sarl-orchestrator
  sarl-orchestrator-critical
  research-sage
  docs-scribe
  sarl-governor
  sarl-stack-steward
  code-builder
  codex-builder
  code-reviewer
  code-reviewer-critical
  qa-agent
  ops-foundation
  community-manager
  support-agent
  bureau-etudes-agent
  designer-3d-agent
  cpanel-watch-agent
  security-audit-agent
)

[[ "$EUID" -eq 0 ]] || {
  echo "Run as root." >&2
  exit 1
}

cd "$ROOT"

docker compose config --quiet
timeout 120 ./scripts/healthcheck.sh

python3 -m unittest discover -s hooks/tests -v
docker exec -u hermes sarl-hermes-agent \
  sh -lc '/opt/sarl-hooks/sarl-policy-guard.py < /opt/sarl-hooks/tests/fixtures/dangerous-terminal.json' \
  | grep -q '"action": "block"'

set -a
source .secrets/project-memory.env
set +a
SARL_MEMORY_TEST_DATABASE_URL="$SARL_MEMORY_DATABASE_URL" \
  services/project-memory-mcp/.venv/bin/python \
  -m unittest discover -s services/project-memory-mcp/tests -v

docker cp scripts/semantic-memory-smoke-test.py \
  sarl-project-memory-mcp:/tmp/semantic-memory-smoke-test.py
docker exec sarl-project-memory-mcp \
  python /tmp/semantic-memory-smoke-test.py

./scripts/test-create-worktree.sh

for profile in "${ACTIVE_PROFILES[@]}"; do
  docker exec -u hermes sarl-hermes-agent \
    "$HERMES" -p "$profile" hooks doctor >/dev/null
  docker exec -u hermes sarl-hermes-agent \
    "$HERMES" -p "$profile" mcp test sarl_project_memory >/dev/null
done

docker exec -u hermes sarl-hermes-agent \
  docker run --rm nikolaik/python-nodejs:python3.11-nodejs20 \
  sh -lc 'python --version >/dev/null; node --version >/dev/null; git --version >/dev/null'

test "$(systemctl is-enabled sarl-agent-ai-cron-tick.timer)" = "enabled"
test "$(systemctl is-active sarl-agent-ai-cron-tick.timer)" = "active"
test "$(systemctl is-enabled sarl-workspace-janitor.timer)" = "enabled"
test "$(systemctl is-active sarl-workspace-janitor.timer)" = "active"
systemctl start sarl-agent-ai-cron-tick.service
systemctl start sarl-workspace-janitor.service

COUNTS="$(
  sudo -u postgres psql -d sarl_agent_memory -Atqc \
    "select count(*) from projects; select count(*) from project_memory; select count(*) from project_memory_chunks;"
)"
test "$COUNTS" = $'0\n0\n0'

test -z "$(find projects -mindepth 1 -maxdepth 1 \
  ! -name '.gitkeep' ! -name 'reports' -print -quit)"

LATEST_BACKUP="$(
  find backups/hermes -mindepth 1 -maxdepth 1 -type d \
    -name '20*T*Z' | sort | tail -1
)"
[[ -n "$LATEST_BACKUP" ]]
./scripts/verify-backup.sh "$LATEST_BACKUP"

echo "SARL_ACCEPTANCE_OK"
