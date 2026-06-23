#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/CascadeProjects/SARL-agent-ai"
BACKUP="${1:-}"
CONFIRM="${2:-}"

if [[ "$EUID" -ne 0 ]]; then
  echo "Run as root." >&2
  exit 1
fi

if [[ -z "$BACKUP" || "$CONFIRM" != "--confirm" ]]; then
  echo "Usage: $0 /absolute/path/to/backup --confirm" >&2
  exit 2
fi

if [[ ! -f "$BACKUP/SHA256SUMS" ]]; then
  echo "Invalid backup: missing SHA256SUMS" >&2
  exit 1
fi

cd "$BACKUP"
sha256sum -c SHA256SUMS

cd "$ROOT"
docker compose stop

if [[ -f "$BACKUP/images/hermes-agent-image.tar" ]]; then
  docker load -i "$BACKUP/images/hermes-agent-image.tar"
fi
if [[ -f "$BACKUP/images/hermes-workspace-image.tar" ]]; then
  docker load -i "$BACKUP/images/hermes-workspace-image.tar"
fi
if [[ -f "$BACKUP/images/project-memory-mcp-image.tar" ]]; then
  docker load -i "$BACKUP/images/project-memory-mcp-image.tar"
fi
if [[ -f "$BACKUP/images/sandbox-docker-image.tar" ]]; then
  docker load -i "$BACKUP/images/sandbox-docker-image.tar"
fi
if [[ -f "$BACKUP/images/sandbox-runtime-image.tar" ]]; then
  docker load -i "$BACKUP/images/sandbox-runtime-image.tar"
fi

tar --acls --xattrs --numeric-owner \
  -xzf "$BACKUP/project-files.tar.gz" \
  -C "$ROOT"

rm -rf /var/lib/docker/volumes/sarl-agent-ai_hermes-agent-data/_data/*
tar --acls --xattrs --numeric-owner \
  -xzf "$BACKUP/volumes/hermes-agent-data.tar.gz" \
  -C /var/lib/docker/volumes/sarl-agent-ai_hermes-agent-data/_data

if [[ -f "$BACKUP/volumes/hermes-workspace-files.tar.gz" ]] \
  && [[ -d /var/lib/docker/volumes/sarl-agent-ai_hermes-workspace-files/_data ]]; then
  rm -rf /var/lib/docker/volumes/sarl-agent-ai_hermes-workspace-files/_data/*
  tar --acls --xattrs --numeric-owner \
    -xzf "$BACKUP/volumes/hermes-workspace-files.tar.gz" \
    -C /var/lib/docker/volumes/sarl-agent-ai_hermes-workspace-files/_data
fi

if [[ -f "$BACKUP/database/sarl_agent_memory.dump" ]]; then
  sudo -u postgres pg_restore \
    --clean --if-exists --no-owner \
    -d sarl_agent_memory \
    "$BACKUP/database/sarl_agent_memory.dump"
fi

docker compose up -d
"$ROOT/scripts/healthcheck.sh"
