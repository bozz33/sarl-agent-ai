#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${SARL_SANDBOX_RUNTIME_IMAGE:-sarl/sandbox-runtime:python3.11-nodejs20-playwright}"

cd "$ROOT"
docker build -t "$IMAGE" deploy/sandbox-runtime
docker save "$IMAGE" | docker exec -i sarl-sandbox-docker \
  docker -H unix:///opt/sandbox-shared/docker.sock load
docker exec -u hermes sarl-hermes-agent docker image inspect "$IMAGE" >/dev/null
docker exec -u hermes sarl-hermes-agent docker run --rm "$IMAGE" \
  sh -lc 'python --version >/dev/null; node --version >/dev/null; npx playwright --version >/dev/null; NODE_PATH="$(npm root -g)" node -e "const { chromium } = require(\"playwright\"); (async () => { const browser = await chromium.launch({ headless: true }); await browser.close(); })();"'
echo "Sandbox runtime ready: $IMAGE"
