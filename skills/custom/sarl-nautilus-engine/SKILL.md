---
name: sarl-nautilus-engine
description: Encadrer l'usage de NautilusTrader dans le module trading via services/nautilus-runner. Impose BacktestEngine, marchés/stratégies allow-listés, aucun TradingNode, aucun live, artefacts obligatoires, basé sur la doc officielle NautilusTrader.
---

# Skill — sarl-nautilus-engine

## Objectif

Garantir que toute exécution NautilusTrader passe par `services/nautilus-runner`
en mode backtest/simulation, conformément à la documentation officielle.

## Quand utiliser

Dès qu'une mission implique de lancer ou configurer un backtest NautilusTrader.

## Règles

- Décisions moteur basées sur la doc officielle (`docs/trading/SOURCES.md`).
- v1 : `BacktestEngine` low-level, venue `SIM`, marchés et stratégies allow-listés.
- Bars `EXTERNAL` BID + ASK (sinon ordres rejetés NO_LIQUIDITY_SIDE).
- IBKR Paper est autorisé uniquement via `nautilus-runner`, en validation/fetch
  read-only, jamais depuis Hermes directement.
- Jamais : `TradingNode`, `LiveNode`, connecteur broker direct, ordre live.
- Artefacts obligatoires : `summary.json`, `orders/fills/positions/account_report.csv`.

## Contrat d'appel runner

```
validate-environment | run-backtest --strategy <allow-listée> --dataset <id> | generate-report --last
```

`nautilus-runner` refuse toute stratégie hors allow-list et tout mot-clé live
(`app/guards.py`). Voir `docs/trading/NAUTILUS-RUNNER-ADAPTER.md`.
