# 20 — NautilusTrader Reports

## Rapports moteur
`engine.trader.generate_{orders,fills,positions,account}_report()` -> DataFrames
exportés en CSV. Tearsheet HTML avec l'extra `visualization`.

## Lecture
- orders : statut (FILLED/REJECTED...), côté, quantité.
- fills : exécutions réelles (vide = aucun fill, signe d'un problème de liquidité).
- positions : ouvertes/fermées, PnL.
- account : équité, solde.

## Artefacts SARL
Par backtest : `summary.json` + 4 CSV dans `reports/backtests/BT-<id>/`.
Digests quotidiens/hebdo via `app/reports.py`, persistés au journal.

## Apprentissage
Le `trading-journal-agent` résume les rapports, calcule les stats et propose des
améliorations (validation humaine requise pour tout changement de règle).
