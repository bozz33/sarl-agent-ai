"""Configuration for nautilus-runner (backtest/simulation only)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = SERVICE_ROOT / "reports" / "backtests"
DATA_DIR = SERVICE_ROOT / "data"
STRATEGIES_DIR = SERVICE_ROOT / "strategies"

# Strategies the runner is allowed to execute. Anything else is refused.
# Each entry maps an allow-listed id to its import paths for the high-level
# (BacktestNode) path.
STRATEGY_SPECS = {
    "eurusd_ema_cross": {
        "strategy_path": "nautilus_trader.examples.strategies.ema_cross:EMACross",
        "config_path": "nautilus_trader.examples.strategies.ema_cross:EMACrossConfig",
        "params": {"fast_ema_period": 10, "slow_ema_period": 20},
    },
    "eurusd_ema_atr": {
        "strategy_path": "strategies.eurusd_ema_atr:EmaAtr",
        "config_path": "strategies.eurusd_ema_atr:EmaAtrConfig",
        "params": {
            "fast_ema_period": 10,
            "slow_ema_period": 20,
            "rsi_period": 14,
            "atr_period": 14,
            "rsi_overbought": 70.0,
            "rsi_oversold": 30.0,
            "atr_no_trade": 0.002,
            "atr_stop_mult": 2.0,
            "rr": 1.5,
        },
    },
    "bollinger_mr": {
        "strategy_path": "strategies.bollinger_mr:BollingerMr",
        "config_path": "strategies.bollinger_mr:BollingerMrConfig",
        "params": {
            "bb_period": 20, "bb_k": 2.0, "rsi_period": 14, "er_period": 10,
            "atr_period": 14, "rsi_oversold": 35.0, "rsi_overbought": 65.0,
            "er_range_max": 0.35, "atr_stop_mult": 2.0,
        },
        "family": "mean-reversion",
    },
    "donchian_break": {
        "strategy_path": "strategies.donchian_break:DonchianBreak",
        "config_path": "strategies.donchian_break:DonchianBreakConfig",
        "params": {
            "dc_period": 20, "er_period": 10, "atr_period": 14,
            "er_trend_min": 0.4, "atr_stop_mult": 2.0, "rr": 2.0,
        },
        "family": "breakout",
    },
}
ALLOWED_STRATEGIES = set(STRATEGY_SPECS)

# Markets allowed (forex majors). Seed = a realistic base price for the
# synthetic generator; IBKR real data overrides it per market.
MARKET_SEEDS = {
    "EUR/USD": 1.10,
    "GBP/USD": 1.27,
    "USD/JPY": 157.0,
}
ALLOWED_MARKETS = set(MARKET_SEEDS)


@dataclass(frozen=True)
class RunnerSettings:
    environment: str = field(default_factory=lambda: os.environ.get("NAUTILUS_ENVIRONMENT", "BACKTEST").upper())
    live_enabled: bool = field(default_factory=lambda: os.environ.get("TRADING_LIVE_ENABLED", "false").lower() == "true")
    kill_switch: bool = field(default_factory=lambda: os.environ.get("TRADING_KILL_SWITCH", "false").lower() == "true")
    paper_only: bool = field(default_factory=lambda: os.environ.get("TRADING_PAPER_ONLY", "true").lower() == "true")

    def as_dict(self) -> dict:
        return {
            "environment": self.environment,
            "live_enabled": self.live_enabled,
            "kill_switch": self.kill_switch,
            "paper_only": self.paper_only,
            "allowed_strategies": sorted(ALLOWED_STRATEGIES),
            "allowed_markets": sorted(ALLOWED_MARKETS),
        }
