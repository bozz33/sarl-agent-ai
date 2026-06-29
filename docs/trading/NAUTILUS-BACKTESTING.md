# NAUTILUS-BACKTESTING.md

## Concept (doc officielle)
Un `BacktestEngine` traite un flux de données historiques puis produit
résultats et métriques une fois le flux terminé. Le chemin recommandé pour la
production est le high-level `BacktestNode` + `ParquetDataCatalog` (les
stratégies se portent ensuite vers `TradingNode` — hors périmètre v1).

## Implémentation v1 (low-level)
1. `BacktestEngine(BacktestEngineConfig(trader_id="BACKTESTER-001"))`.
2. Venue `SIM` : `add_venue(OmsType.NETTING, AccountType.MARGIN, base USD, 1_000_000 USD)`.
3. Instrument : `TestInstrumentProvider.default_fx_ccy("EUR/USD", venue)`.
4. Données : bars **BID + ASK** `EXTERNAL` (le matching engine FX a besoin des
   deux pour remplir un ordre marché ; sinon `NO_LIQUIDITY_SIDE`).
5. Stratégie : `EMACross` (allow-listée `eurusd_ema_cross`).
6. `engine.run()` -> `engine.get_result()` + rapports `engine.trader.generate_*`.

## Artefacts produits
`summary.json`, `orders_report.csv`, `fills_report.csv`,
`positions_report.csv`, `account_report.csv`.

## Piège résolu
Bars pré-construites = source `EXTERNAL` (pas `INTERNAL`, qui est réservé à
l'agrégation interne). Une seule série BID = ordres rejetés.

## Évolution
Passer à `BacktestNode` + `ParquetDataCatalog` avec données historiques réelles,
ajouter walk-forward avant toute conclusion.
