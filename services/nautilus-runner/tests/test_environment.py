"""Environment must be able to run NautilusTrader backtests."""

from app import config


def test_nautilus_importable():
    import nautilus_trader
    from nautilus_trader.backtest.node import BacktestNode  # noqa: F401
    from nautilus_trader.backtest.engine import BacktestEngine  # noqa: F401

    assert nautilus_trader.__version__


def test_settings_default_paper():
    s = config.RunnerSettings()
    assert s.paper_only is True
    assert s.live_enabled is False
    assert s.environment in {"BACKTEST", "SIMULATION"}
