# nautilus-runner: secured backtest adapter. Backtest/simulation only.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NAUTILUS_ENVIRONMENT=BACKTEST \
    TRADING_PAPER_ONLY=true \
    TRADING_LIVE_ENABLED=false \
    TRADING_KILL_SWITCH=false

WORKDIR /srv

COPY pyproject.toml ./
RUN pip install --no-cache-dir "nautilus_trader>=1.230.0" "pandas>=2.2" "mcp>=1.27,<2" "ib_async>=2.0" "pytest>=8.0"

COPY app ./app
COPY strategies ./strategies
COPY tests ./tests

# Fail the build if the no-live guard tests do not pass.
RUN python -m pytest -q tests/test_no_live_tools.py

# MCP server defaults (Hermes reaches it over streamable-HTTP at /mcp).
ENV NAUTILUS_MCP_TRANSPORT=streamable-http \
    NAUTILUS_MCP_HOST=0.0.0.0 \
    NAUTILUS_MCP_PORT=8200

EXPOSE 8200

# Default: run the MCP server. CLI usage: override command, e.g.
#   docker run ... python -m app.main run-backtest
ENTRYPOINT ["python"]
CMD ["-m", "app.mcp_server"]
