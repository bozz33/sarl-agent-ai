"""HTML tearsheet rendering (pure Python, no engine)."""

from app import viz


def test_equity_svg_handles_empty_and_data():
    assert "No closed trades" in viz._equity_svg([])
    svg = viz._equity_svg([10.0, -5.0, 7.0])
    assert "<svg" in svg and "polyline" in svg


def test_render_html_contains_stats_and_no_live():
    summary = {
        "backtest_id": "BT-TEST",
        "strategy": "eurusd_ema_atr",
        "market": "EUR/USD",
        "dataset": "realistic_eurusd",
        "data_provenance": "realistic-random-walk",
        "engine_api": "BacktestNode+ParquetDataCatalog",
        "bars": 5000,
        "total_orders": 216,
        "total_positions": 108,
        "live": False,
        "stats_pnls_usd": {"PnL (total)": "-1866.39", "Win Rate": "0.36"},
    }
    out = viz.render_html(summary, [1.0, -2.0, 3.0])
    assert "BT-TEST" in out
    assert "eurusd_ema_atr" in out
    assert "BACKTEST ONLY" in out
    assert "live=false" in out
    assert "Win Rate" in out
