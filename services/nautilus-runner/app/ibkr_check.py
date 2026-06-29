"""Phase 7 — IBKR PAPER connection check (read-only, paper-only).

Connects to the IB Gateway paper API, proves the account is a PAPER account
(IBKR paper account ids start with 'DU'), and returns a short summary. No order
is ever placed here. Fails closed: any non-paper account or live flag aborts.

Run only after .secrets/ibkr.env is filled and the ib-gateway container is up
(2FA approved). Uses ib_async (the maintained ib_insync successor).
"""

from __future__ import annotations

import os

from app import guards

HOST = os.environ.get("IBKR_HOST", "ib-gateway")
PORT = int(os.environ.get("IBKR_PORT", "4002"))  # 4002 = paper API
CLIENT_ID = int(os.environ.get("IBKR_CLIENT_ID", "7"))


def check_ibkr_paper() -> dict:
    """Connect to IB Gateway paper, assert paper account, return a summary."""
    # Hard gate first: this module is paper-only and must never enable live.
    guards.assert_paper_only()
    if os.environ.get("TRADING_LIVE_ENABLED", "false").lower() == "true":
        raise guards.LivePathBlocked("TRADING_LIVE_ENABLED=true is forbidden.")

    try:
        from ib_async import IB
    except Exception as exc:  # dependency not installed
        return {"ok": False, "reason": f"ib_async not available: {exc}"}

    ib = IB()
    try:
        ib.connect(HOST, PORT, clientId=CLIENT_ID, timeout=15)
    except Exception as exc:
        return {"ok": False, "reason": f"cannot reach IB Gateway at {HOST}:{PORT}: {exc}",
                "hint": "fill .secrets/ibkr.env, start ib-gateway, approve the 2FA push"}

    try:
        accounts = list(ib.managedAccounts())
        # IBKR paper account ids start with 'DU'. Live ids start with 'U'.
        paper = all(a.startswith("DU") for a in accounts) and bool(accounts)
        if not paper:
            raise guards.LivePathBlocked(f"Non-paper account(s) detected: {accounts}. Refusing.")
        summary = {row.tag: row.value for row in ib.accountSummary() if row.tag in
                   ("AccountType", "NetLiquidation", "AvailableFunds", "Currency")}
        return {
            "ok": True,
            "account_mode": "PAPER",
            "accounts": accounts,
            "summary": summary,
            "gateway": f"{HOST}:{PORT}",
            "live": False,
        }
    finally:
        ib.disconnect()
