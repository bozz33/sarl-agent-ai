"""Daily / weekly report generation from the trading journal.

Reads the SQLite journal and produces markdown digests (and a Telegram-ready
short form). No live data, no external calls here — the journal-agent ships
the digest to Telegram via the SARL bridge.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app import journal


def _rows(conn: sqlite3.Connection, query: str, params: tuple = ()) -> list[tuple]:
    return conn.execute(query, params).fetchall()


def daily_report(db_path: str | Path = journal.DEFAULT_DB, since_hours: int = 24) -> str:
    """Markdown digest of backtests + learning proposals in the window."""
    journal.init_db(db_path)
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).isoformat()
    conn = journal.connect(db_path)
    try:
        bts = _rows(conn, "SELECT id, strategy, market, summary_json FROM backtests WHERE created_at >= ? ORDER BY created_at", (cutoff,))
        lps = _rows(conn, "SELECT id, proposal, governor_status FROM learning_proposals WHERE created_at >= ?", (cutoff,))
        blocks = _rows(conn, "SELECT blocking_rule FROM risk_blocks WHERE created_at >= ?", (cutoff,))
    finally:
        conn.close()

    lines = [
        "# TRADING DEMO — DAILY REPORT",
        f"Date: {datetime.now(timezone.utc):%Y-%m-%d}",
        "Mode: BACKTEST / SIMULATION ONLY",
        f"Backtests: {len(bts)}",
        f"Risk blocks: {len(blocks)}",
        f"Learning proposals: {len(lps)}",
        "",
    ]
    for bt_id, strat, market, summary_json in bts:
        try:
            s = json.loads(summary_json)
            pnl = s.get("stats_pnls_usd", {}).get("PnL (total)", "n/a")
        except Exception:
            pnl = "n/a"
        lines.append(f"- {bt_id} · {strat} · {market} · orders/positions tracked · PnL(USD)={pnl}")
    if not bts:
        lines.append("- no backtests in window")
    lines.append("")
    lines.append("Live orders: 0 (forbidden). Action required: human review of any rule-change proposal.")
    body = "\n".join(lines)

    _persist(db_path, "daily", body)
    return body


def weekly_report(db_path: str | Path = journal.DEFAULT_DB) -> str:
    return daily_report(db_path, since_hours=24 * 7).replace("DAILY REPORT", "WEEKLY REPORT")


def _persist(db_path: str | Path, kind: str, body: str) -> None:
    conn = journal.connect(db_path)
    try:
        rid = f"{kind.upper()}-{uuid.uuid4().hex[:8]}"
        table = "daily_reports" if kind == "daily" else "weekly_reports"
        conn.execute(f"INSERT INTO {table} (id, created_at, body_md) VALUES (?,?,?)",
                     (rid, datetime.now(timezone.utc).isoformat(), body))
        conn.commit()
    finally:
        conn.close()
