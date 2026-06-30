"""Phase 7 — fetch REAL historical EUR/USD bars from IBKR (paper, read-only).

Pulls historical forex bars via ib_async and writes them as a CSV into
data/historical/ so the catalog backtest can run on REAL market data
(dataset='ibkr_eurusd'). No order is ever placed. Forex has no real volume
(IBKR returns -1) so a constant placeholder volume is written.
"""

from __future__ import annotations

import os
from pathlib import Path

from app import config, guards

HOST = os.environ.get("IBKR_HOST", "ib-gateway")
PORT = int(os.environ.get("IBKR_PORT", "4004"))
CLIENT_ID = int(os.environ.get("IBKR_DATA_CLIENT_ID", "52"))

HISTORICAL_DIR = config.DATA_DIR / "historical"


def _dataset_name(market: str) -> str:
    return "ibkr_" + market.replace("/", "").lower()


def fetch_ibkr_eurusd(duration: str = "2 D", bar_size: str = "1 min",
                      name: str | None = None, market: str = "EUR/USD") -> dict:
    """Fetch real bars for *market* from IBKR paper into data/historical/<name>.csv."""
    guards.assert_paper_only()
    if os.environ.get("TRADING_LIVE_ENABLED", "false").lower() == "true":
        raise guards.LivePathBlocked("TRADING_LIVE_ENABLED=true is forbidden.")
    name = name or _dataset_name(market)
    symbol = market.replace("/", "")

    try:
        from ib_async import IB, Forex, util
    except Exception as exc:
        return {"ok": False, "reason": f"ib_async not available: {exc}"}

    ib = IB()
    try:
        ib.connect(HOST, PORT, clientId=CLIENT_ID, timeout=25)
    except Exception as exc:
        return {"ok": False, "reason": f"cannot reach IB Gateway at {HOST}:{PORT}: {exc}"}

    try:
        # Prove we are on a PAPER account before pulling anything.
        accounts = list(ib.managedAccounts())
        if not (accounts and all(a.startswith("DU") for a in accounts)):
            raise guards.LivePathBlocked(f"Non-paper account(s): {accounts}. Refusing.")

        ib.reqMarketDataType(3)  # delayed is fine for historical without a subscription
        contract = Forex(symbol)
        ib.qualifyContracts(contract)
        bars = ib.reqHistoricalData(
            contract, endDateTime="", durationStr=duration,
            barSizeSetting=bar_size, whatToShow="MIDPOINT",
            useRTH=False, formatDate=2,
        )
        df = util.df(bars)
        if df is None or len(df) == 0:
            return {"ok": False, "reason": "IBKR returned no historical data"}

        out = df[["date", "open", "high", "low", "close"]].copy()
        out = out.rename(columns={"date": "timestamp"})
        out["volume"] = 1_000_000  # forex has no real volume (IBKR returns -1)

        HISTORICAL_DIR.mkdir(parents=True, exist_ok=True)
        path = HISTORICAL_DIR / f"{name}.csv"
        out.to_csv(path, index=False)
        return {
            "ok": True,
            "market": market,
            "dataset": name,
            "csv": str(path),
            "bars": int(len(out)),
            "first": str(out["timestamp"].iloc[0]),
            "last": str(out["timestamp"].iloc[-1]),
            "account_mode": "PAPER",
            "live": False,
        }
    finally:
        ib.disconnect()
