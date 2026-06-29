"""IBKR paper check must fail closed and gracefully without a gateway."""

import os

from app import ibkr_check


def test_no_gateway_fails_gracefully(monkeypatch):
    # Point at an unreachable host so connect() fails fast, not crashes.
    monkeypatch.setenv("IBKR_HOST", "127.0.0.1")
    monkeypatch.setenv("IBKR_PORT", "4999")
    import importlib

    importlib.reload(ibkr_check)
    out = ibkr_check.check_ibkr_paper()
    assert out["ok"] is False
    assert "reason" in out


def test_live_flag_blocked(monkeypatch):
    monkeypatch.setenv("TRADING_LIVE_ENABLED", "true")
    import importlib

    importlib.reload(ibkr_check)
    from app import guards

    try:
        ibkr_check.check_ibkr_paper()
        assert False, "should have blocked"
    except guards.LivePathBlocked:
        pass
    finally:
        monkeypatch.delenv("TRADING_LIVE_ENABLED", raising=False)
        importlib.reload(ibkr_check)
