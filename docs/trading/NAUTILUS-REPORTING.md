# NAUTILUS-REPORTING.md

## Rapports NautilusTrader
Le moteur produit ordres, fills, positions et état de compte. Exportés par
`engine.trader.generate_{orders,fills,positions,account}_report()` en CSV.
Tearsheet HTML possible avec l'extra `visualization`.

## Artefacts SARL par backtest
`services/nautilus-runner/reports/backtests/BT-<id>/` :
- `summary.json` (id, stratégie, marché, ordres, positions, stats PnL, live=false)
- `orders_report.csv`, `fills_report.csv`, `positions_report.csv`, `account_report.csv`

## Digests
- `app/reports.py` : `daily_report()` / `weekly_report()` lisent le journal et
  produisent un markdown ; persistés dans `daily_reports` / `weekly_reports`.
- Le `trading-journal-agent` envoie le digest court à Telegram via le bridge SARL.

## Format digest quotidien
```
TRADING DEMO — DAILY REPORT
Date / Mode: BACKTEST ONLY
Backtests / Risk blocks / Learning proposals
- <BT-id> · stratégie · marché · PnL(USD)
Live orders: 0 (forbidden). Action required: ...
```
