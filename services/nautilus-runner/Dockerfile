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
RUN pip install --no-cache-dir nautilus_trader>=1.230.0 pandas>=2.2 pytest>=8.0

COPY app ./app
COPY strategies ./strategies
COPY tests ./tests

# Fail the build if the no-live guard tests do not pass.
RUN python -m pytest -q tests/test_no_live_tools.py

ENTRYPOINT ["python", "-m", "app.main"]
CMD ["validate-environment"]
