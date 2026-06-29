# 18 — NautilusTrader Backtesting

## Deux API
- Low-level `BacktestEngine` : contrôle fin (utilisé en v1).
- High-level `BacktestNode` + `ParquetDataCatalog` : recommandé pour la
  production, portable vers `TradingNode` (cible future).

## Pipeline v1 (résumé)
1. Engine + config.
2. Venue `SIM` (NETTING, MARGIN, USD).
3. Instrument EUR/USD.
4. Bars BID + ASK `EXTERNAL` (sinon `NO_LIQUIDITY_SIDE`).
5. Stratégie EMA cross.
6. `run()` -> résultats + rapports.

## Métriques
PnL total/%, win rate, expectancy, drawdown (via `get_result`).

## Détail technique
Voir `../NAUTILUS-BACKTESTING.md` (code réel, pièges résolus) et le smoke test
`services/nautilus-runner/tests/test_backtest_smoke.py`.
