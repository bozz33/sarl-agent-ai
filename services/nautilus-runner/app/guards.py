"""Security guards for nautilus-runner.

This module is the hard boundary that keeps the Trading Demo Lab in
backtest/simulation only. No live trading path may pass these checks.
The rule: a forbidden keyword anywhere in a request, strategy file, or
config aborts the mission and is logged for the Governor.
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Absolute policy -------------------------------------------------------
LIVE_FORBIDDEN = True
ALLOWED_ENVIRONMENTS = {"BACKTEST", "SIMULATION"}

# Any of these appearing in a strategy/config/request means a live path is
# being attempted. v1 forbids all of them.
FORBIDDEN_KEYWORDS = [
    "TradingNode",
    "LiveNode",
    "TradingNodeConfig",
    "LiveDataClient",
    "LiveExecClient",
    "LiveExecutionEngine",
    "connect_live",
    "place_live_order",
    "cancel_live_order",
    "modify_live_order",
    "IBKR_LIVE",
    "InteractiveBrokersExecClient",
    "live_account",
    "real_money",
]


class LivePathBlocked(RuntimeError):
    """Raised when a live trading path is detected. Never caught silently."""


def assert_paper_only() -> None:
    """Fail closed unless the environment proves backtest/simulation mode."""
    if not LIVE_FORBIDDEN:
        raise LivePathBlocked("LIVE_FORBIDDEN flag was flipped; refusing to run.")

    if os.environ.get("TRADING_KILL_SWITCH", "false").lower() == "true":
        raise LivePathBlocked("TRADING_KILL_SWITCH=true; module disabled.")

    if os.environ.get("TRADING_LIVE_ENABLED", "false").lower() == "true":
        raise LivePathBlocked("TRADING_LIVE_ENABLED=true is not allowed in v1.")

    env = os.environ.get("NAUTILUS_ENVIRONMENT", "BACKTEST").upper()
    if env not in ALLOWED_ENVIRONMENTS:
        raise LivePathBlocked(f"Environment {env!r} not in {ALLOWED_ENVIRONMENTS}.")


def scan_text(text: str, source: str = "request") -> None:
    """Raise if any forbidden keyword is present in *text*."""
    lowered = text.lower()
    for kw in FORBIDDEN_KEYWORDS:
        if kw.lower() in lowered:
            raise LivePathBlocked(f"Forbidden keyword {kw!r} found in {source}.")


def scan_path(path: str | Path) -> None:
    """Scan a file (e.g. a strategy) for forbidden live paths."""
    p = Path(path)
    if not p.exists():
        return
    scan_text(p.read_text(encoding="utf-8", errors="ignore"), source=str(p))


def scan_strategies_dir(directory: str | Path) -> list[str]:
    """Scan every *.py strategy file. Returns the list of scanned files."""
    d = Path(directory)
    scanned: list[str] = []
    if not d.exists():
        return scanned
    for py in sorted(d.glob("*.py")):
        scan_path(py)
        scanned.append(py.name)
    return scanned
