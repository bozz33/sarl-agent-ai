# nautilus-runner

Secured adapter between Hermes and **NautilusTrader**. Part of the
`sarl-module-trading-demo` module of SARL-Agent-AI. **Backtest / simulation
only.** No `TradingNode`, no `LiveNode`, no broker, no real money.

## Why it exists
Hermes never calls NautilusTrader directly and never talks to a broker.
Hermes asks this service for an allow-listed action; the service runs the
hard guards (`app/guards.py`), then runs the backtest, then returns
verifiable artifacts (summary.json + CSV reports). Any live path is refused.

## Commands
```bash
python -m app.main validate-environment
python -m app.main run-backtest --strategy eurusd_ema_cross --dataset simulated_eurusd
python -m app.main generate-report --last
```

## v1 scope
- Engine: NautilusTrader `BacktestEngine` (low-level), SIM venue.
- Market: EUR/USD only (allow-listed).
- Strategy: `eurusd_ema_cross` (EMA cross, allow-listed).
- Data: deterministic synthetic bars (`app/data.py`). Real historical data
  plugs in later via `ParquetDataCatalog`.

## Tests
```bash
pip install nautilus_trader pandas pytest
python -m pytest -q
```
The Docker build fails if `tests/test_no_live_tools.py` does not pass.

## Guarantees enforced in code
- `guards.assert_paper_only()` fails closed on kill-switch, `TRADING_LIVE_ENABLED`,
  or any non-backtest environment.
- `guards.scan_*` reject any forbidden live keyword in strategies/configs/requests.
- No live tool exists in this service. Adding one is a guarded, reviewed change.

## Definition of done
A task is done only with **file + passing test + report + git diff** — never
an agent's self-declaration. See `docs/trading/ACCEPTANCE-TESTS.md`.
