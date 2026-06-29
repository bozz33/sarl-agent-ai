# NAUTILUS-RUNNER-ADAPTER.md

`services/nautilus-runner` is the secured layer between Hermes and NautilusTrader.

## Responsibilities
1. Receive an allow-listed action from Hermes.
2. Run the hard guards (`assert_paper_only`, keyword scans, allow-lists).
3. Prepare data (synthetic in v1; `ParquetDataCatalog` later).
4. Run `BacktestEngine` (low-level) on the SIM venue.
5. Generate artifacts: `summary.json`, `orders_report.csv`, `fills_report.csv`,
   `positions_report.csv`, `account_report.csv`.
6. Return the summary. Refuse anything live.

## Module map
```
app/guards.py    security boundary (no-live, allow-lists, fail-closed)
app/config.py    settings + allow-listed strategies/markets
app/data.py      deterministic synthetic EUR/USD bars (v1)
app/runner.py    BacktestEngine wiring + artifact export
app/main.py      CLI: validate-environment | run-backtest | generate-report
strategies/eurusd_ema_cross.py   allow-listed EMA-cross strategy
tests/           no-live, environment, backtest smoke
```

## v1 engine choices (per official NautilusTrader docs)
- Low-level `BacktestEngine` with a simulated `SIM` venue.
- EUR/USD instrument via `TestInstrumentProvider.default_fx_ccy`.
- Bars fed as `EXTERNAL` BID + ASK series (matching engine needs both to fill
  FX market orders), wrangled by `BarDataWrangler`.
- Strategy: bundled `EMACross` example, allow-listed under id `eurusd_ema_cross`.
- Later: migrate to high-level `BacktestNode` + `ParquetDataCatalog` with real
  historical data, then (Phase 7) IBKR **paper** via the `ib` extra — never live.

## CLI contract
```
validate-environment  -> guards pass + nautilus version + settings
run-backtest          -> runs + writes artifacts + returns summary.json
generate-report --last-> prints the latest summary.json
```

## Definition of done
file + passing test + report + git diff. Never an agent's self-declaration.
