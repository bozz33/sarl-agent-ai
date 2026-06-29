"""EUR/USD EMA cross strategy (v1, backtest only).

Thin wrapper around NautilusTrader's bundled EMACross example so the
runner has a stable, allow-listed strategy id. No live path here.
"""

from __future__ import annotations

from nautilus_trader.examples.strategies.ema_cross import EMACross, EMACrossConfig

__all__ = ["EMACross", "EMACrossConfig"]
