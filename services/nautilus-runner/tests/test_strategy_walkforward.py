"""Enriched strategy + walk-forward validation (backtest only)."""

from app.catalog_runner import run_catalog_backtest
from app.walk_forward import walk_forward


def test_enriched_strategy_runs_and_filters():
    s = run_catalog_backtest(strategy="eurusd_ema_atr", dataset="realistic_eurusd")
    assert s["live"] is False
    assert s["strategy"] == "eurusd_ema_atr"
    assert s["total_orders"] > 0
    assert s["total_positions"] > 0
    # Filters (RSI + ATR no-trade) must reduce overtrading vs the naive cross.
    naive = run_catalog_backtest(strategy="eurusd_ema_cross", dataset="realistic_eurusd")
    assert s["total_orders"] < naive["total_orders"]


def test_walk_forward_produces_oos_folds():
    wf = walk_forward(strategy="eurusd_ema_atr", dataset="realistic_eurusd", folds=4)
    assert wf["live"] is False
    assert len(wf["fold_results"]) == 4
    for f in wf["fold_results"]:
        assert f["bars"] > 0
    agg = wf["aggregate"]
    assert "mean_pnl" in agg
    assert "profitable_folds" in agg
    assert "consistent" in agg
