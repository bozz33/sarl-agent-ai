"""EUR/USD bar generation / loading.

Three sources, in order of realism:
- `synthetic_eurusd_bars`  : deterministic trend+sine (smoke test only; gives an
  artificially clean result — never use for performance conclusions).
- `realistic_eurusd_bars`  : seeded geometric random walk (GBM) — credible,
  non-perfect results; default for the catalog backtest.
- `load_csv_bars`          : REAL historical data. Drop a CSV with columns
  timestamp,open,high,low,close,volume into data/historical/ and it is used.

No network dependency. Real market data = drop a CSV (see `dataset_dataframe`).
"""

from __future__ import annotations

import math
from pathlib import Path

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


HISTORICAL_DIR = Path(__file__).resolve().parent.parent / "data" / "historical"


def realistic_eurusd_bars(periods: int = 5000, seed: float = 1.10, freq: str = "1min", rng_seed: int = 42) -> pd.DataFrame:
    """Seeded geometric random walk — credible (non-perfect) EUR/USD bars.

    Realistic intraday volatility and no engineered trend, so a trend-following
    strategy gets a believable mix of wins and losses (unlike the sine smoke).
    """
    import numpy as np

    rng = np.random.default_rng(rng_seed)
    index = pd.date_range("2024-01-01", periods=periods, freq=freq, tz="UTC")
    # ~1 bp per-minute volatility, tiny drift.
    rets = rng.normal(loc=0.0, scale=0.0001, size=periods)
    close = seed * np.exp(np.cumsum(rets))
    open_ = np.empty(periods)
    open_[0] = seed
    open_[1:] = close[:-1]
    noise = np.abs(rng.normal(0.0, 0.00008, size=periods))
    high = np.maximum(open_, close) + noise
    low = np.minimum(open_, close) - noise
    df = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": 1_000_000},
        index=index,
    )
    return df


def load_csv_bars(path: str | Path) -> pd.DataFrame:
    """Load REAL historical bars from a CSV (timestamp,open,high,low,close,volume)."""
    df = pd.read_csv(path)
    ts_col = next((c for c in df.columns if c.lower() in ("timestamp", "time", "date", "datetime")), df.columns[0])
    df[ts_col] = pd.to_datetime(df[ts_col], utc=True)
    df = df.set_index(ts_col)
    df.columns = [c.lower() for c in df.columns]
    if "volume" not in df.columns:
        df["volume"] = 1_000_000
    return df[["open", "high", "low", "close", "volume"]]


def dataset_dataframe(dataset: str) -> tuple[pd.DataFrame, str]:
    """Resolve a dataset name to a DataFrame + a provenance label.

    - 'real' or a CSV name in data/historical/ -> real historical data.
    - 'realistic_eurusd' (default) -> seeded random walk.
    - 'simulated_eurusd' -> the deterministic sine smoke series.
    """
    if dataset in ("simulated_eurusd",):
        return synthetic_eurusd_bars(), "synthetic-sine"
    # Real data: a CSV dropped in data/historical/ takes precedence.
    if HISTORICAL_DIR.exists():
        candidates = sorted(HISTORICAL_DIR.glob("*.csv"))
        if dataset == "real" and candidates:
            return load_csv_bars(candidates[0]), f"real-csv:{candidates[0].name}"
        named = HISTORICAL_DIR / f"{dataset}.csv"
        if named.exists():
            return load_csv_bars(named), f"real-csv:{named.name}"
    return realistic_eurusd_bars(), "realistic-random-walk"
