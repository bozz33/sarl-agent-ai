# TRADING-JOURNAL-SCHEMA.md

SQLite journal of the demo lab. Implemented in
`services/nautilus-runner/app/journal.py`. Never deleted. No live data.

## Location
`services/nautilus-runner/data/journal.db` (gitignored; recreated by `init_db`).
A repo-level copy may also live at `data/trading/journal.db`.

## Tables
- `signals` — id, created_at, market, timeframe, direction, reason, context, decision
- `backtests` — id, created_at, engine, strategy, market, dataset_ref, config_ref,
  result_path, summary_json, status, git_commit
- `trades` — id, backtest_id, market, direction, entry, exit, pnl_r, result
- `risk_blocks` — id, created_at, context, blocking_rule
- `daily_reports` — id, created_at, body_md
- `weekly_reports` — id, created_at, body_md
- `learning_proposals` — id, created_at, source_backtest_id, proposal, risk_review,
  governor_status, **human_validation_required (default 1)**, status
- `governor_reviews` — id, created_at, subject, decision, notes

## API
```python
from app import journal
journal.init_db()                       # create all tables
journal.write_backtest(summary)         # record a backtest run
journal.write_learning_proposal(text, source_backtest_id=bt_id)
```

## Rule
Every learning proposal requires human validation by default
(`human_validation_required = 1`). The runner writes the backtest summary to the
journal automatically after each run. Important lessons are promoted to the
project memory (MCP) by `trading-journal-agent`.
