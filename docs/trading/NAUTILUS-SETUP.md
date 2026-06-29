# NAUTILUS-SETUP.md

Installation et exécution de NautilusTrader dans le module (backtest only).

## Prérequis (doc officielle)
- Python 3.12 à 3.14. Recommandé : `uv` + venv.
- Linux : glibc ≥ 2.35. (Vérifié : glibc 2.39 OK, NautilusTrader 1.230.0 OK.)

## Installation
```bash
uv pip install nautilus_trader              # base
uv pip install "nautilus_trader[visualization]"   # + tearsheets HTML
# phase future IBKR uniquement :
uv pip install "nautilus_trader[ib,docker]"
```

## Dans SARL
Le service `services/nautilus-runner` épingle `nautilus_trader>=1.230.0` dans
`pyproject.toml` et tourne en container `python:3.12-slim`. Aucune install
manuelle requise : `docker build services/nautilus-runner`.

## Smoke test
```bash
python -m app.main validate-environment
python -m app.main run-backtest --strategy eurusd_ema_cross --dataset simulated_eurusd
python -m pytest -q
```

## MCP server
```bash
NAUTILUS_MCP_TRANSPORT=streamable-http python -m app.mcp_server
# écoute sur :8200/mcp
```
