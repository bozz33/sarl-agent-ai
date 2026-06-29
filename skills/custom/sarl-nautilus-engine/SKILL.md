---
name: sarl-nautilus-engine
description: Encadrer l'usage de NautilusTrader dans le module trading via services/nautilus-runner. Impose BacktestNode/BacktestEngine, ParquetDataCatalog, EUR/USD, aucun TradingNode, aucun live, artefacts obligatoires, basé sur la doc officielle NautilusTrader.
---

# Skill — sarl-nautilus-engine

## Objectif

Garantir que toute exécution NautilusTrader passe par `services/nautilus-runner`
en mode backtest/simulation, conformément à la documentation officielle.

## Quand utiliser

Dès qu'une mission implique de lancer ou configurer un backtest NautilusTrader.

## Règles

- Décisions moteur basées sur la doc officielle (`docs/trading/SOURCES.md`).
- v1 : `BacktestEngine` low-level, venue `SIM`, EUR/USD, stratégie `eurusd_ema_cross`.
- Bars `EXTERNAL` BID + ASK (sinon ordres rejetés NO_LIQUIDITY_SIDE).
- Plus tard : `BacktestNode` + `ParquetDataCatalog` avec données historiques réelles.
- Jamais : `TradingNode`, `LiveNode`, connecteur broker, IBKR en v1.
- Artefacts obligatoires : `summary.json`, `orders/fills/positions/account_report.csv`.

## Contrat d'appel runner

```
validate-environment | run-backtest --strategy <allow-listée> --dataset <id> | generate-report --last
```

`nautilus-runner` refuse toute stratégie hors allow-list et tout mot-clé live
(`app/guards.py`). Voir `docs/trading/NAUTILUS-RUNNER-ADAPTER.md`.
