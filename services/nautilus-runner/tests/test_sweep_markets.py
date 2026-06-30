"""Multi-market backtest + bounded sweep (backtest only)."""

from app.catalog_runner import run_catalog_backtest
from app.sweep import run_sweep
from app import config


def test_all_markets_trade():
    # Each allow-listed market must actually produce trades (relative ATR gate).
    for market in config.ALLOWED_MARKETS:
        s = run_catalog_backtest(strategy="eurusd_ema_atr", dataset="realistic", market=market)
        assert s["market"] == market
        assert s["live"] is False
        assert s["total_orders"] > 0


def test_sweep_ranks_and_is_not_live():
    r = run_sweep(markets=["EUR/USD"], max_combos=4)
    assert r["live"] is False
    assert r["ran"] > 0
    assert isinstance(r["top"], list)
    if r["best"]:
        assert "strategy" in r["best"] and "params" in r["best"]
