---
name: sarl-trading-journal
description: Journaliser signaux, backtests, résultats et leçons du module trading dans data/trading/journal.db, et produire les rapports quotidiens/hebdomadaires. Permet l'apprentissage tracé sans modifier les règles actives.
---

# Skill — sarl-trading-journal

## Objectif

Tracer tout signal, backtest et résultat pour permettre l'apprentissage, et
produire des rapports lisibles.

## Quand utiliser

Après chaque backtest/analyse, et pour les digests quotidiens/hebdomadaires.

## Chaque entrée doit contenir

date · marché · timeframe · stratégie · contexte · hypothèse · résultat ·
métriques (PnL R, drawdown, win rate) · erreurs · leçon.

## Formats imposés

```
BACKTEST_RESULT:
BACKTEST_ID:
STRATEGY:
MARKET:
BARS:
ORDERS:
POSITIONS:
PNL_R:
DRAWDOWN:
RULES_RESPECTED:
ERRORS:
LESSON:
MEMORY_WRITE_REQUIRED:
```

## Stockage

`data/trading/journal.db` (SQLite). Tables : signals, backtests, orders,
positions, trades, risk_blocks, daily_reports, weekly_reports,
learning_proposals, governor_reviews. Leçons importantes -> MCP mémoire projet.

## Garde-fou

Le journal n'est jamais supprimé. Écrire un fait ne modifie aucune règle active.
