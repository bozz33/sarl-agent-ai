#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="$ROOT/runtime-observability"
REPORT="$REPORT_DIR/latest.txt"

mkdir -p "$REPORT_DIR"
chmod 0755 "$REPORT_DIR"
TMP="$(mktemp "$REPORT_DIR/.latest.XXXXXX")"
trap 'rm -f "$TMP"' EXIT

cd "$ROOT"
{
  printf 'COLLECTED_AT_UTC=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'HOST_UPTIME='
  uptime
  printf 'ROOT_DISK='
  df -P /root | awk 'NR==2 {printf "used=%s available_kb=%s\n", $5, $4}'
  printf 'MEMORY='
  free -m | awk '/^Mem:/ {printf "used_mb=%s available_mb=%s total_mb=%s\n", $3, $7, $2}'

  echo
  echo '[COMPOSE]'
  docker ps \
    --filter label=com.docker.compose.project=sarl-agent-ai \
    --format '{{.Names}} image={{.Image}} status={{.Status}} ports={{.Ports}}'

  echo
  echo '[ENDPOINTS]'
  printf 'hermes_health='
  curl -fsS --max-time 10 http://127.0.0.1:8642/health
  echo
  printf 'workspace_http='
  curl -fsS -o /dev/null -w '%{http_code}\n' --max-time 10 http://127.0.0.1:3000/

  echo
  echo '[TIMERS]'
  for timer in \
    sarl-agent-ai-cron-tick.timer \
    sarl-workspace-janitor.timer \
    sarl-agent-ai-telegram-work-sync.timer; do
    printf '%s active=%s enabled=%s\n' \
      "$timer" \
      "$(systemctl is-active "$timer" 2>&1 || true)" \
      "$(systemctl is-enabled "$timer" 2>&1 || true)"
  done

  echo
  echo '[RECENT_LOG_COUNTS_30M]'
  for container in \
    sarl-hermes-agent \
    sarl-hermes-workspace \
    sarl-project-memory-mcp \
    sarl-sandbox-docker; do
    logs="$(docker logs --since 30m "$container" 2>&1 || true)"
    errors="$(printf '%s\n' "$logs" | grep -Eic 'error|exception|traceback|critical' || true)"
    warnings="$(printf '%s\n' "$logs" | grep -Eic 'warning|warn' || true)"
    printf '%s errors=%s warnings=%s\n' "$container" "$errors" "$warnings"
  done

  echo
  echo '[CRON_TICK]'
  systemctl show sarl-agent-ai-cron-tick.service \
    --property=ActiveState,Result,ExecMainStatus,StateChangeTimestamp \
    --no-pager
} >"$TMP"

chmod 0644 "$TMP"
mv -f "$TMP" "$REPORT"
mkdir -p "$ROOT/reports/platform-health"
chmod 0755 "$ROOT/reports" "$ROOT/reports/platform-health"
cp "$REPORT" "$ROOT/reports/platform-health/latest.txt"
chmod 0644 "$ROOT/reports/platform-health/latest.txt"
trap - EXIT
printf '%s\n' "$REPORT"
