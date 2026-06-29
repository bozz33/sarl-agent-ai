"""The journal schema must be creatable and writable (SQLite, stdlib only)."""

import sqlite3

from app import journal


def test_init_creates_all_tables(tmp_path):
    db = tmp_path / "journal.db"
    journal.init_db(db)
    conn = sqlite3.connect(db)
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    finally:
        conn.close()
    names = {r[0] for r in rows}
    for table in journal.TABLES:
        assert table in names


def test_write_backtest_and_proposal(tmp_path):
    db = tmp_path / "journal.db"
    journal.init_db(db)
    summary = {
        "backtest_id": "BT-TEST-0001",
        "engine": "NautilusTrader",
        "strategy": "eurusd_ema_cross",
        "market": "EUR/USD",
        "dataset": "simulated_eurusd",
        "report_dir": "/tmp/x",
    }
    bt_id = journal.write_backtest(summary, db_path=db)
    assert bt_id == "BT-TEST-0001"

    lp_id = journal.write_learning_proposal("try ATR filter", source_backtest_id=bt_id, db_path=db)
    assert lp_id.startswith("LP-")

    conn = sqlite3.connect(db)
    try:
        bt = conn.execute("SELECT strategy FROM backtests WHERE id=?", (bt_id,)).fetchone()
        lp = conn.execute("SELECT human_validation_required FROM learning_proposals WHERE id=?", (lp_id,)).fetchone()
    finally:
        conn.close()
    assert bt[0] == "eurusd_ema_cross"
    # Learning proposals must require human validation by default.
    assert lp[0] == 1
