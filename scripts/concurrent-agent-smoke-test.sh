#!/usr/bin/env bash
set -euo pipefail

HERMES="/opt/hermes/.venv/bin/hermes"
CONTAINER="sarl-hermes-agent"
PROFILES=(
  sarl-router
  research-sage
  code-reviewer
  support-agent
  bureau-etudes-agent
)

RESULT_DIR="$(mktemp -d /tmp/sarl-agent-concurrency.XXXXXX)"
trap 'rm -rf "$RESULT_DIR"' EXIT
START_MS="$(date +%s%3N)"

pids=()
for profile in "${PROFILES[@]}"; do
  marker="CONCURRENT_OK_${profile//-/_}"
  (
    docker exec -u hermes "$CONTAINER" \
      "$HERMES" -p "$profile" -z \
      "Test concurrent sans projet. N'utilise aucun outil. Réponds uniquement par : $marker" \
      > "$RESULT_DIR/$profile.out"
  ) &
  pids+=("$!")
done

for pid in "${pids[@]}"; do
  wait "$pid"
done

for profile in "${PROFILES[@]}"; do
  marker="CONCURRENT_OK_${profile//-/_}"
  grep -q "$marker" "$RESULT_DIR/$profile.out"
done

ELAPSED_MS="$(( $(date +%s%3N) - START_MS ))"
echo "CONCURRENT_AGENT_SMOKE_OK agents=${#PROFILES[@]} elapsed_ms=$ELAPSED_MS"
