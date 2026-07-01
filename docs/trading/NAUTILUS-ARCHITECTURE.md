# NAUTILUS-ARCHITECTURE.md

## Vue d'ensemble
```
trading agents (Hermes)
  -> MCP sarl_nautilus_runner (streamable-HTTP :8200/mcp)
  -> services/nautilus-runner
       app/guards.py    barrière no-live (fail closed)
       app/config.py    allow-lists strategies/markets
       app/data.py      bars synthétiques déterministes
       app/ibkr_*.py    validation/fetch IBKR Paper read-only
       app/runner.py    BacktestEngine + export artefacts
       app/journal.py   SQLite (signals/backtests/.../learning_proposals)
       app/reports.py   digests daily/weekly
       app/scheduler.py missions bornées (pas de boucle infinie)
       app/main.py      CLI
       app/mcp_server.py serveur MCP (tools allow-listés)
  -> NautilusTrader BacktestEngine (venue SIM)
```

## Principes
- Hermes ne parle jamais à NautilusTrader ni à un broker directement.
- Une seule frontière sécurité : `guards.py` + allow-lists + gate de build.
- v1 : `BacktestEngine` low-level. Données synthétiques + IBKR Paper read-only
  pour validation/fetch historique quand la passerelle est disponible.
- Aucun `TradingNode`/`LiveNode`/broker live.

## Flux d'un backtest
guards -> venue SIM + marché allow-listé -> bars BID+ASK EXTERNAL -> stratégie
allow-listée -> run -> summary.json + CSV reports -> journal.

Voir `NAUTILUS-RUNNER-ADAPTER.md`, `NAUTILUS-MCP-INTEGRATION.md`.
