"""The security boundary must hold: no live path may pass."""

import os

import pytest

from app import config, guards


def test_live_forbidden_flag():
    assert guards.LIVE_FORBIDDEN is True
    assert guards.ALLOWED_ENVIRONMENTS == {"BACKTEST", "SIMULATION"}


def test_forbidden_keywords_present():
    for kw in ("TradingNode", "LiveNode", "place_live_order", "real_money"):
        assert kw in guards.FORBIDDEN_KEYWORDS


@pytest.mark.parametrize("text", [
    "build a TradingNode",
    "from x import LiveExecClient",
    "place_live_order(123)",
    "enable real_money mode",
])
def test_scan_text_blocks_live(text):
    with pytest.raises(guards.LivePathBlocked):
        guards.scan_text(text)


def test_strategies_dir_is_clean():
    # Real v1 strategies must contain no live keyword.
    scanned = guards.scan_strategies_dir(config.STRATEGIES_DIR)
    assert "eurusd_ema_cross.py" in scanned


def test_assert_paper_only_passes_default(monkeypatch):
    for var in ("TRADING_KILL_SWITCH", "TRADING_LIVE_ENABLED", "NAUTILUS_ENVIRONMENT"):
        monkeypatch.delenv(var, raising=False)
    guards.assert_paper_only()  # should not raise


@pytest.mark.parametrize("var,val", [
    ("TRADING_KILL_SWITCH", "true"),
    ("TRADING_LIVE_ENABLED", "true"),
    ("NAUTILUS_ENVIRONMENT", "LIVE"),
])
def test_assert_paper_only_blocks(monkeypatch, var, val):
    monkeypatch.setenv(var, val)
    with pytest.raises(guards.LivePathBlocked):
        guards.assert_paper_only()
