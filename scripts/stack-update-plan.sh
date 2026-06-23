#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/CascadeProjects/SARL-agent-ai"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="$ROOT/reports/stack-updates/stack-audit-$STAMP.txt"

cd "$ROOT"
{
  echo "SARL-Agent-AI stack audit $STAMP"
  echo
  docker compose ps
  echo
  docker images --digests \
    sarl/hermes-agent \
    ghcr.io/outsourc-e/hermes-workspace
  echo
  curl -fsS http://127.0.0.1:8642/health
  echo
  curl -fsS http://127.0.0.1:3000/api/auth-check
  echo
  git status --short 2>/dev/null || true
} > "$REPORT"

echo "$REPORT"

