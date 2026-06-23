#!/usr/bin/env bash
set -euo pipefail

HERMES="/opt/hermes/.venv/bin/hermes"
CONTAINER="sarl-hermes-agent"
PROFILES=(
  sarl-router
  sarl-orchestrator
  sarl-orchestrator-critical
  research-sage
  docs-scribe
  sarl-governor
  sarl-stack-steward
  code-reviewer-critical
  code-reviewer
  ops-foundation
  community-manager
  support-agent
  bureau-etudes-agent
  designer-3d-agent
)

run_until_marker() {
  local profile="$1"
  local marker="$2"
  local prompt="$3"
  local result=""

  for attempt in 1 2; do
    result="$(
      docker exec -u hermes "$CONTAINER" \
        "$HERMES" -p "$profile" -z "$prompt" || true
    )"
    if grep -q "$marker" <<<"$result"; then
      printf '%s' "$result"
      return 0
    fi
    sleep 2
  done

  printf '%s\n' "$result" >&2
  return 1
}

for profile in "${PROFILES[@]}"; do
  marker="PROFILE_OK_${profile//-/_}"
  run_until_marker \
    "$profile" \
    "$marker" \
    "Test de santé sans projet. N'utilise aucun outil et ne crée aucun fichier. Réponds uniquement par : $marker" \
    >/dev/null || {
    echo "Profile smoke test failed: $profile" >&2
    exit 1
  }
  echo "$profile OK"
done

for profile in code-builder codex-builder qa-agent; do
  marker="SANDBOX_OK_${profile//-/_}"
  run_until_marker \
    "$profile" \
    "$marker" \
    "Test sans projet. Utilise le terminal sandbox Docker pour exécuter python --version et node --version. Ne crée aucun fichier. Si les deux commandes réussissent, réponds avec le marqueur $marker." \
    >/dev/null || {
    echo "Sandbox agent workflow failed: $profile" >&2
    exit 1
  }
  echo "$profile sandbox OK"
done

echo "MODEL_WORKFLOW_SMOKE_OK"
