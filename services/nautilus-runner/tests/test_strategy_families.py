"""The strategy families (trend, mean-reversion, breakout) all run, no live."""

import pytest

from app import config
from app.catalog_runner import run_catalog_backtest


@pytest.mark.parametrize("strategy", ["bollinger_mr", "donchian_break"])
def test_new_families_run(strategy):
    s = run_catalog_backtest(strategy=strategy, dataset="realistic", market="EUR/USD", resample="15min")
    assert s["live"] is False
    assert s["strategy"] == strategy
    # Regime-filtered: may trade few times, but must not error.
    assert s["total_orders"] >= 0


def test_allow_list_has_four_families():
    assert {"eurusd_ema_cross", "eurusd_ema_atr", "bollinger_mr", "donchian_break"} <= config.ALLOWED_STRATEGIES
