"""SQLite trading journal for the demo lab.

Records signals, backtests, results and lessons so the module can learn.
Append-only in spirit: the journal is never deleted. No live data here.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "journal.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS signals (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  market TEXT NOT NULL,
  timeframe TEXT,
  direction TEXT,
  reason TEXT,
  context TEXT,
  decision TEXT NOT NULL DEFAULT 'PAPER_ONLY'
);

CREATE TABLE IF NOT EXISTS backtests (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  engine TEXT NOT NULL,
  strategy TEXT NOT NULL,
  market TEXT NOT NULL,
  dataset_ref TEXT NOT NULL,
  config_ref TEXT,
  result_path TEXT NOT NULL,
  summary_json TEXT NOT NULL,
  status TEXT NOT NULL,
  git_commit TEXT
);

CREATE TABLE IF NOT EXISTS trades (
  id TEXT PRIMARY KEY,
  backtest_id TEXT,
  market TEXT,
  direction TEXT,
  entry REAL,
  exit REAL,
  pnl_r REAL,
  result TEXT,
  FOREIGN KEY (backtest_id) REFERENCES backtests(id)
);

CREATE TABLE IF NOT EXISTS risk_blocks (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  context TEXT NOT NULL,
  blocking_rule TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_reports (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  body_md TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weekly_reports (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  body_md TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS learning_proposals (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  source_backtest_id TEXT,
  proposal TEXT NOT NULL,
  risk_review TEXT,
  governor_status TEXT NOT NULL DEFAULT 'PENDING',
  human_validation_required INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'PROPOSED'
);

CREATE TABLE IF NOT EXISTS governor_reviews (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  subject TEXT NOT NULL,
  decision TEXT NOT NULL,
  notes TEXT
);
"""

TABLES = [
    "signals", "backtests", "trades", "risk_blocks",
    "daily_reports", "weekly_reports", "learning_proposals", "governor_reviews",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str | Path = DEFAULT_DB) -> Path:
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
    return Path(db_path)


def write_backtest(summary: dict, db_path: str | Path = DEFAULT_DB, git_commit: str | None = None) -> str:
    conn = connect(db_path)
    try:
        bt_id = summary.get("backtest_id") or f"BT-{uuid.uuid4().hex[:8]}"
        conn.execute(
            "INSERT OR REPLACE INTO backtests "
            "(id, created_at, engine, strategy, market, dataset_ref, result_path, summary_json, status, git_commit) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                bt_id,
                summary.get("created_at", _now()),
                summary.get("engine", "NautilusTrader"),
                summary.get("strategy", ""),
                summary.get("market", ""),
                summary.get("dataset", ""),
                summary.get("report_dir", ""),
                json.dumps(summary),
                "DONE",
                git_commit,
            ),
        )
        conn.commit()
        return bt_id
    finally:
        conn.close()


def write_learning_proposal(proposal: str, source_backtest_id: str | None = None,
                            db_path: str | Path = DEFAULT_DB) -> str:
    conn = connect(db_path)
    try:
        lp_id = f"LP-{uuid.uuid4().hex[:8]}"
        conn.execute(
            "INSERT INTO learning_proposals (id, created_at, source_backtest_id, proposal) VALUES (?,?,?,?)",
            (lp_id, _now(), source_backtest_id, proposal),
        )
        conn.commit()
        return lp_id
    finally:
        conn.close()
