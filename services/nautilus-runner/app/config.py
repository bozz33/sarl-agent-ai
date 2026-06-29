"""Configuration for nautilus-runner (backtest/simulation only)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = SERVICE_ROOT / "reports" / "backtests"
DATA_DIR = SERVICE_ROOT / "data"
STRATEGIES_DIR = SERVICE_ROOT / "strategies"

# Strategies the runner is allowed to execute in v1. Anything else is refused.
ALLOWED_STRATEGIES = {"eurusd_ema_cross"}

# Markets allowed in v1.
ALLOWED_MARKETS = {"EUR/USD"}


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
