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
