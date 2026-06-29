"""High-level catalog backtest must run and give credible (non-perfect) results."""

from app.catalog_runner import run_catalog_backtest


def test_catalog_backtest_runs():
    s = run_catalog_backtest(dataset="realistic_eurusd")
    assert s["live"] is False
    assert s["engine_api"] == "BacktestNode+ParquetDataCatalog"
    assert s["data_provenance"] == "realistic-random-walk"
    assert s["bars"] > 0
    assert s["total_orders"] > 0
    assert s["total_positions"] > 0


def test_realistic_data_is_not_artificially_perfect():
    # The realistic random walk must NOT produce a 100% win rate (that was the
    # tell-tale sign of the synthetic sine series).
    s = run_catalog_backtest(dataset="realistic_eurusd")
    win_rate = s["stats_pnls_usd"].get("Win Rate")
    assert win_rate is not None
    assert 0.0 < float(win_rate) < 1.0
