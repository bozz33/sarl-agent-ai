# NO-LIVE-TOOLS.md

## Policy (v1)

```
No live tool exists in the module.
No TradingNode active.
No LiveNode active.
No broker connection.
No real order path.
```

## Enforcement (in code, not just docs)
`services/nautilus-runner/app/guards.py`:
- `LIVE_FORBIDDEN = True` and `ALLOWED_ENVIRONMENTS = {"BACKTEST", "SIMULATION"}`.
- `assert_paper_only()` fails closed on `TRADING_KILL_SWITCH`, `TRADING_LIVE_ENABLED`,
  or any non-backtest environment.
- `scan_text` / `scan_path` / `scan_strategies_dir` reject any of:
  `TradingNode, LiveNode, TradingNodeConfig, LiveDataClient, LiveExecClient,
  LiveExecutionEngine, connect_live, place_live_order, cancel_live_order,
  modify_live_order, IBKR_LIVE, InteractiveBrokersExecClient, live_account,
  real_money`.
- The Docker build runs `tests/test_no_live_tools.py` and fails if it does not pass.

## Forbidden runner actions (must not exist)
```
nautilus_start_live
nautilus_run_trading_node
nautilus_connect_live_broker
nautilus_connect_ibkr_live
nautilus_place_live_order
nautilus_modify_live_order
nautilus_cancel_live_order
nautilus_enable_real_money
```

## If a live path is detected
```
block -> raise LivePathBlocked
log   -> Governor review
refuse the mission
```

Adding any live capability later is a separate, human-validated change with
its own review and a new wrapper — never a silent edit here.
