FROM nousresearch/hermes-agent:v2026.6.19@sha256:9f367c7756ef087661a361536a89f438d57a122b958dc23d82d456b1433e6e9e

RUN uv pip install --python /opt/hermes/.venv/bin/python --no-cache ddgs==9.14.4

# Anthropic OAuth initial-login token endpoint fix.
# The pinned image posts the first token exchange to console.anthropic.com,
# which now returns 404; the endpoint moved to platform.claude.com. The refresh
# path in the same file already uses platform.claude.com, so this only aligns the
# initial login. Remove once the base image ships the corrected endpoint.
RUN sed -i 's#_OAUTH_TOKEN_URL = "https://console.anthropic.com/v1/oauth/token"#_OAUTH_TOKEN_URL = "https://platform.claude.com/v1/oauth/token"#' /opt/hermes/agent/anthropic_adapter.py \
    && grep -q 'https://platform.claude.com/v1/oauth/token' /opt/hermes/agent/anthropic_adapter.py

# WhatsApp bridge (Baileys) dependencies. The bridge lives under the root-owned
# image path, so the runtime user cannot install node_modules at pairing time
# (EACCES). Install at build instead; the gateway user only needs to read them.
RUN cd /opt/hermes/scripts/whatsapp-bridge \
    && (npm ci --omit=dev || npm install --omit=dev) \
    && test -d node_modules \
    && python3 -c "import hashlib; open('node_modules/.hermes-pkg-hash','w').write(hashlib.sha256(open('package.json','rb').read()).hexdigest()[:16])"

# --- SARL: dev/quality runtimes for code agents (durable) ---
# Closes the runtime gaps found in the 2026-06-29 readiness audit so code
# agents can run the per-project quality gates (lint/typecheck/test) and JS
# tooling. PHP/composer are intentionally NOT added: WordPress/PHP work runs
# in the project container, keeping hermes-agent lean. Playwright stays driven
# by the internal browser tool against the pinned browser binaries already in
# /opt/hermes/.playwright; project e2e uses the project's own pinned playwright.

# jq for JSON/shell scripting in agent terminals.
RUN apt-get update \
    && apt-get install -y --no-install-recommends jq \
    && rm -rf /var/lib/apt/lists/* \
    && jq --version

# pnpm via corepack (Node 22 ships corepack) for JS/TS projects.
RUN corepack enable pnpm \
    && corepack prepare pnpm@latest --activate \
    && pnpm --version

# Python quality tools, installed isolated (each in its own env via uv tool)
# so they never conflict with the hermes runtime venv. Entrypoints land on
# /usr/local/bin (already on PATH).
ENV UV_TOOL_BIN_DIR=/usr/local/bin
RUN uv tool install ruff \
    && uv tool install mypy \
    && uv tool install pytest \
    && ruff --version && mypy --version && pytest --version

# `pip` shim -> uv. The base image manages Python with uv and ships no system
# pip; this stops `pip install ...` from hard-failing inside agent sessions.
RUN printf '#!/bin/sh\nexec uv pip "$@"\n' > /usr/local/bin/pip \
    && chmod +x /usr/local/bin/pip \
    && ln -sf /usr/local/bin/pip /usr/local/bin/pip3
