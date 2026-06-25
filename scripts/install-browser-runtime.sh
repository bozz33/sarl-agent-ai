#!/usr/bin/env bash
# Install the Chrome for Testing runtime used by the browser_* tools.
#
# The agent-browser native binary and Chrome system libraries already ship in the
# hermes-agent image, but Chrome for Testing is downloaded into the runtime user's
# home (HERMES_HOME=/opt/data), which is a Docker volume that masks the image. This
# script provisions Chrome into that volume so the browser tools work for agents,
# which run as the hermes user. It is idempotent: agent-browser skips the download
# when Chrome is already present.
set -euo pipefail

CONTAINER="${1:-sarl-hermes-agent}"
AGENT_BROWSER="/opt/hermes/node_modules/agent-browser/bin/agent-browser-linux-x64"

docker exec -u hermes -e HOME=/opt/data "$CONTAINER" "$AGENT_BROWSER" install

echo "Verifying real browser launch..."
docker exec -u hermes -e HOME=/opt/data "$CONTAINER" "$AGENT_BROWSER" open https://example.com >/dev/null
docker exec -u hermes -e HOME=/opt/data "$CONTAINER" "$AGENT_BROWSER" snapshot | head -1
echo "Browser runtime ready."
