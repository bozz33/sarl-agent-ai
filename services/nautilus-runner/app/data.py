"""Synthetic EUR/USD bar generation for the v1 smoke backtest.

No external data dependency: a deterministic trend + oscillation series so
backtests are reproducible. Real historical data plugs in later via the
ParquetDataCatalog (Phase 3+).
"""

from __future__ import annotations

import math

import pandas as pd


def synthetic_eurusd_bars(periods: int = 2000, seed: float = 1.10, freq: str = "1min") -> pd.DataFrame:
    """Return an OHLCV DataFrame indexed by UTC timestamps.

    Deterministic: a slow trend plus a sine oscillation gives EMA crossings
    so the strategy actually trades during the smoke test.
    """
    index = pd.date_range("2024-01-01", periods=periods, freq=freq, tz="UTC")
    rows = []
    price = seed
    for i in range(periods):
        trend = 0.00002 * i
        wave = 0.0040 * math.sin(i / 60.0)
        mid = seed + trend + wave
        spread = 0.00010
        open_ = mid
        close = seed + trend + 0.0040 * math.sin((i + 1) / 60.0)
        high = max(open_, close) + spread
        low = min(open_, close) - spread
        rows.append((open_, high, low, close, 1_000_000))
        price = close
    df = pd.DataFrame(rows, index=index, columns=["open", "high", "low", "close", "volume"])
    return df
