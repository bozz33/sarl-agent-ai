"""End-to-end smoke: the runner produces real, verifiable artifacts."""

import json
from pathlib import Path

from app.runner import run_backtest


def test_backtest_runs_and_produces_artifacts():
    summary = run_backtest()

    # Real execution, not a stub.
    assert summary["live"] is False
    assert summary["market"] == "EUR/USD"
    assert summary["bars"] > 0
    assert summary["total_orders"] > 0
    assert summary["total_positions"] > 0

    out = Path(summary["report_dir"])
    assert (out / "summary.json").exists()
    assert (out / "orders_report.csv").exists()
    assert (out / "fills_report.csv").exists()
    assert (out / "positions_report.csv").exists()
    assert (out / "account_report.csv").exists()

    # summary.json is valid and consistent.
    data = json.loads((out / "summary.json").read_text())
    assert data["backtest_id"] == summary["backtest_id"]
    assert data["engine"] == "NautilusTrader"
