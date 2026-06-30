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

-- Persistent strategy candidates: the autonomous research loop upserts here so
-- a config's robustness is judged over MANY runs, not a single backtest. A
-- candidate is "proven" only after surviving walk-forward repeatedly.
-- Key/value state for the autonomous loop (iteration counter, window count).
CREATE TABLE IF NOT EXISTS loop_state (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS strategy_candidates (
  id TEXT PRIMARY KEY,             -- hash of strategy+market+timeframe+params
  strategy TEXT NOT NULL,
  market TEXT NOT NULL,
  timeframe TEXT NOT NULL,
  params_json TEXT NOT NULL,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  times_tested INTEGER NOT NULL DEFAULT 0,
  times_robust INTEGER NOT NULL DEFAULT 0,
  last_robust_score REAL,
  best_robust_score REAL,
  proven INTEGER NOT NULL DEFAULT 0
);
"""

TABLES = [
    "signals", "backtests", "trades", "risk_blocks",
    "daily_reports", "weekly_reports", "learning_proposals", "governor_reviews",
    "strategy_candidates",
]

# A candidate is "proven" only after surviving walk-forward this many times,
# at this minimum robust-survival ratio. Repeated out-of-sample survival, not
# one lucky backtest.
PROVEN_MIN_ROBUST = 3
PROVEN_MIN_RATIO = 0.6


def upsert_candidate(strategy: str, market: str, timeframe: str, params: dict,
                     is_robust: bool, robust_score: float, db_path: str | Path = DEFAULT_DB) -> dict:
    """Record a candidate observation; promote to proven after repeated survival."""
    import hashlib

    key = hashlib.sha256(f"{strategy}|{market}|{timeframe}|{json.dumps(params, sort_keys=True)}".encode()).hexdigest()[:16]
    conn = connect(db_path)
    try:
        row = conn.execute("SELECT times_tested, times_robust, best_robust_score FROM strategy_candidates WHERE id=?", (key,)).fetchone()
        now = _now()
        if row is None:
            conn.execute(
                "INSERT INTO strategy_candidates (id, strategy, market, timeframe, params_json, "
                "first_seen, last_seen, times_tested, times_robust, last_robust_score, best_robust_score, proven) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (key, strategy, market, timeframe, json.dumps(params, sort_keys=True), now, now,
                 1, 1 if is_robust else 0, robust_score, robust_score, 0),
            )
            tested, robust, best = 1, 1 if is_robust else 0, robust_score
        else:
            tested = row[0] + 1
            robust = row[1] + (1 if is_robust else 0)
            best = max(row[2] if row[2] is not None else -1e9, robust_score)
            conn.execute(
                "UPDATE strategy_candidates SET last_seen=?, times_tested=?, times_robust=?, "
                "last_robust_score=?, best_robust_score=? WHERE id=?",
                (now, tested, robust, robust_score, best, key),
            )
        proven = 1 if (robust >= PROVEN_MIN_ROBUST and robust / tested >= PROVEN_MIN_RATIO) else 0
        conn.execute("UPDATE strategy_candidates SET proven=? WHERE id=?", (proven, key))
        conn.commit()
        return {"id": key, "times_tested": tested, "times_robust": robust, "proven": bool(proven)}
    finally:
        conn.close()


def get_state(key: str, default: str = "0", db_path: str | Path = DEFAULT_DB) -> str:
    conn = connect(db_path)
    try:
        row = conn.execute("SELECT value FROM loop_state WHERE key=?", (key,)).fetchone()
        return row[0] if row else default
    finally:
        conn.close()


def set_state(key: str, value: str, db_path: str | Path = DEFAULT_DB) -> None:
    conn = connect(db_path)
    try:
        conn.execute("INSERT INTO loop_state (key, value) VALUES (?,?) "
                     "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))
        conn.commit()
    finally:
        conn.close()


def robustness_levels(db_path: str | Path = DEFAULT_DB) -> dict:
    """The real-robustness picture: how high each candidate climbed (times_robust
    = number of distinct windows survived) and the current ceiling reached."""
    conn = connect(db_path)
    try:
        cols = ["strategy", "market", "timeframe", "params_json", "times_tested",
                "times_robust", "best_robust_score"]
        rows = conn.execute(
            f"SELECT {','.join(cols)} FROM strategy_candidates "
            "ORDER BY times_robust DESC, best_robust_score DESC LIMIT 12"
        ).fetchall()
        cands = [dict(zip(cols, r)) for r in rows]
        ceiling = max((c["times_robust"] for c in cands), default=0)
        return {"ceiling_level": ceiling, "candidates": cands}
    finally:
        conn.close()


def proven_candidates(db_path: str | Path = DEFAULT_DB) -> list[dict]:
    conn = connect(db_path)
    try:
        cols = ["id", "strategy", "market", "timeframe", "params_json", "times_tested",
                "times_robust", "best_robust_score"]
        rows = conn.execute(
            f"SELECT {','.join(cols)} FROM strategy_candidates WHERE proven=1 "
            "ORDER BY best_robust_score DESC"
        ).fetchall()
        return [dict(zip(cols, r)) for r in rows]
    finally:
        conn.close()


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
