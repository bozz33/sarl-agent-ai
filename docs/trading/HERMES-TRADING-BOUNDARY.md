# HERMES-TRADING-BOUNDARY.md

The hard separation between Hermes and the trading engine.

## Rule

```
Hermes is NOT the trader.
Hermes orchestrates, analyses, controls and journals.
NautilusTrader is the backtest/simulation engine.
services/nautilus-runner is the security barrier.
The Governor protects the system. The human validates dangerous steps.
```

## What Hermes may do
- Read the education corpus (`docs/trading/education/`) and official sources.
- Produce a `TRADING_RESEARCH_NOTE`.
- Propose / edit an allow-listed strategy (reviewed).
- Ask `nautilus-runner` for an allow-listed action (e.g. `run-backtest`).
- Read artifacts, write the journal, propose improvements, open Kanban tasks,
  write validated lessons to memory, produce a Telegram digest.

## What Hermes must NEVER do
- Call NautilusTrader directly.
- Talk to a broker or hold broker credentials.
- Start a `TradingNode` or `LiveNode`.
- Place / modify / cancel a real order.
- Connect IBKR directly or hold IBKR credentials.
- Place / modify / cancel an IBKR paper order without explicit human approval.
- Add a live tool or remove a guard.
- Change a risk rule without human validation.

## Allowed call shape
```
Hermes  ->  nautilus-runner tool (allow-listed)
            e.g. run_backtest(strategy="eurusd_ema_cross", dataset="simulated_eurusd")
nautilus-runner verifies: environment, kill-switch, live disabled,
                          strategy allow-listed, no forbidden keyword
            ->  NautilusTrader BacktestEngine
            ->  artifacts (summary.json + CSV reports)
```

See `NAUTILUS-RUNNER-ADAPTER.md`, `NO-LIVE-TOOLS.md`, `NO-DIRECT-BROKER-ACCESS.md`.
