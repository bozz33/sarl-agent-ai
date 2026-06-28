#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SANDBOX_RUNTIME_IMAGE="${SARL_SANDBOX_RUNTIME_IMAGE:-sarl/sandbox-runtime:python3.11-nodejs20-playwright}"

cd "$ROOT"
docker compose ps
curl -fsS http://127.0.0.1:8642/health
echo
curl -fsS http://127.0.0.1:3000/api/auth-check
echo
WORKSPACE_MAIN_ASSET="$(
  curl -fsS http://127.0.0.1:3000/ \
    | strings \
    | grep -oE '/assets/main-[^" ]+\.js' \
    | head -1
)"
test -n "$WORKSPACE_MAIN_ASSET"
curl -fsSI -H 'Accept-Encoding: gzip' \
  "http://127.0.0.1:3000$WORKSPACE_MAIN_ASSET" \
  | grep -qi '^Content-Encoding: gzip'
docker exec sarl-hermes-agent \
  curl -fsS http://127.0.0.1:9119/api/status
echo
docker exec -u hermes sarl-hermes-agent \
  test -r /workspace
docker exec -u hermes sarl-hermes-agent \
  test -r /opt/custom-skills/sarl-agent-ai-operating-contract/SKILL.md
docker exec -u hermes sarl-hermes-agent \
  test -x /opt/sarl-hooks/sarl-policy-guard.py
docker exec -u workspace sarl-hermes-workspace \
  test -r /workspace
docker exec -u workspace sarl-hermes-workspace \
  sh -lc 'probe="/workspace/.healthcheck-write-$$"; mkdir "$probe"; trap "rm -rf \"$probe\"" EXIT; printf ok > "$probe/probe"; test "$(cat "$probe/probe")" = ok'
test "$(docker inspect sarl-project-memory-mcp \
  --format '{{.State.Health.Status}}')" = "healthy"
test -z "$(docker inspect sarl-project-memory-mcp \
  --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if $conf}}published{{end}}{{end}}')"
test -z "$(docker inspect sarl-sandbox-docker \
  --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if $conf}}published{{end}}{{end}}')"
test "$(docker network inspect sarl-agent-ai_sandbox-control \
  --format '{{.Internal}}')" = "true"
docker exec -u hermes sarl-hermes-agent \
  docker info >/dev/null
docker exec -u hermes sarl-hermes-agent \
  docker image inspect "$SANDBOX_RUNTIME_IMAGE" >/dev/null
docker exec -u hermes sarl-hermes-agent \
  docker run --rm "$SANDBOX_RUNTIME_IMAGE" \
  sh -lc 'python --version >/dev/null && node --version >/dev/null && npx playwright --version >/dev/null && npx playwright install --dry-run chromium | grep -q chromium'
docker exec -u hermes sarl-hermes-agent \
  /opt/hermes/.venv/bin/hermes -p sarl-orchestrator \
  mcp test sarl_project_memory >/dev/null

# Chat missions are persisted automatically under projects/reports so they are
# visible from Workspace. Only actual project roots are forbidden at startup.
test -z "$(find "$ROOT/projects" -mindepth 1 -maxdepth 1 \
  ! -name '.gitkeep' ! -name 'reports' -print -quit)"
test "$(systemctl is-active sarl-workspace-janitor.timer)" = "active"

echo "Healthcheck OK"
