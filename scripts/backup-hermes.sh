#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$ROOT/backups/hermes/$STAMP"
CONSISTENT=false
WITH_IMAGES=false

for arg in "$@"; do
  case "$arg" in
    --consistent) CONSISTENT=true ;;
    --with-images) WITH_IMAGES=true ;;
    *)
      echo "Usage: $0 [--consistent] [--with-images]" >&2
      exit 2
      ;;
  esac
done

if [[ "$EUID" -ne 0 ]]; then
  echo "Run as root." >&2
  exit 1
fi

mkdir -p "$DEST"/{metadata,logs,volumes,images,database}
chmod 700 "$DEST"

cd "$ROOT"
docker compose ps > "$DEST/metadata/docker-compose-ps.txt"
docker compose config > "$DEST/metadata/docker-compose-rendered.yml"
docker inspect sarl-hermes-agent sarl-hermes-workspace \
  sarl-project-memory-mcp sarl-sandbox-docker \
  > "$DEST/metadata/containers-inspect.json"
docker image inspect \
  sarl/hermes-agent:0.17.0-ddgs1 \
  sarl/hermes-workspace:d04e1f3-sarl13-no-global-sse \
  sarl/project-memory-mcp:0.2.1 \
  docker:27-dind@sha256:aa3df78ecf320f5fafdce71c659f1629e96e9de0968305fe1de670e0ca9176ce \
  > "$DEST/metadata/images-inspect.json"
docker compose logs --no-color --timestamps hermes-agent \
  > "$DEST/logs/hermes-agent.log"
docker compose logs --no-color --timestamps hermes-workspace \
  > "$DEST/logs/hermes-workspace.log"
docker compose logs --no-color --timestamps project-memory-mcp \
  > "$DEST/logs/project-memory-mcp.log"
docker compose logs --no-color --timestamps sandbox-docker \
  > "$DEST/logs/sandbox-docker.log"

sudo -u postgres pg_dump -Fc sarl_agent_memory \
  > "$DEST/database/sarl_agent_memory.dump"

tar --acls --xattrs --numeric-owner \
  --exclude='./backups' \
  -czf "$DEST/project-files.tar.gz" \
  .

restart_stack() {
  if [[ "$CONSISTENT" == true ]]; then
    docker compose up -d >/dev/null 2>&1 || true
  fi
}
trap restart_stack EXIT

if [[ "$CONSISTENT" == true ]]; then
  docker compose stop
fi

tar --acls --xattrs --numeric-owner \
  -czf "$DEST/volumes/hermes-agent-data.tar.gz" \
  -C /var/lib/docker/volumes/sarl-agent-ai_hermes-agent-data/_data .

if [[ -d /var/lib/docker/volumes/sarl-agent-ai_hermes-workspace-files/_data ]]; then
  tar --acls --xattrs --numeric-owner \
    -czf "$DEST/volumes/hermes-workspace-files.tar.gz" \
    -C /var/lib/docker/volumes/sarl-agent-ai_hermes-workspace-files/_data .
fi

if [[ "$CONSISTENT" == true ]]; then
  docker compose up -d
  CONSISTENT=false
fi
trap - EXIT

if [[ "$WITH_IMAGES" == true ]]; then
  docker save -o "$DEST/images/hermes-agent-image.tar" \
    sarl/hermes-agent:0.17.0-ddgs1
  docker save -o "$DEST/images/hermes-workspace-image.tar" \
    sarl/hermes-workspace:d04e1f3-sarl13-no-global-sse
  docker save -o "$DEST/images/project-memory-mcp-image.tar" \
    sarl/project-memory-mcp:0.2.1
  docker save -o "$DEST/images/sandbox-docker-image.tar" \
    docker:27-dind@sha256:aa3df78ecf320f5fafdce71c659f1629e96e9de0968305fe1de670e0ca9176ce
  docker save -o "$DEST/images/sandbox-runtime-image.tar" \
    nikolaik/python-nodejs:python3.11-nodejs20
fi

(
  cd "$DEST"
  find . -type f ! -name SHA256SUMS -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    > SHA256SUMS
)

echo "$DEST"
