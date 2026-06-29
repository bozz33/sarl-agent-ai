"""Reports + bounded missions must work and stay backtest-only."""

from app import reports, scheduler


def test_daily_report_from_empty_journal(tmp_path):
    db = tmp_path / "journal.db"
    body = reports.daily_report(db_path=db)
    assert "DAILY REPORT" in body
    assert "BACKTEST / SIMULATION ONLY" in body
    assert "Live orders: 0" in body


def test_missions_are_bounded_and_listed():
    # No hidden missions; only the two bounded ones.
    assert set(scheduler.MISSIONS) == {"daily_trading_demo", "weekly_trading_review"}


def test_unknown_mission_rejected():
    import pytest

    with pytest.raises(ValueError):
        scheduler.run_mission("trade_live_now")


def test_daily_cycle_runs_and_is_not_live():
    out = scheduler.run_mission("daily_trading_demo")
    assert out["live"] is False
    assert out["backtest_id"].startswith("BT-")
    assert out["report_chars"] > 0
