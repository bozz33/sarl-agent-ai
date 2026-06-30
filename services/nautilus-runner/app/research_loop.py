"""Autonomous research loop — escalate robustness LEVEL by LEVEL until it breaks.

The level of a candidate = how many DISTINCT time windows it has survived
walk-forward on. Each iteration tests on a NEW sliding window, so reaching
"level N" means "survived N different periods", not the same backtest repeated.
This reveals the REAL robustness ceiling: candidates climb 3 -> 4 -> 5 -> ... -> n
until a regime they cannot handle knocks them out.

The number of distinct windows grows with available history, so the loop also
(pacing-safely) refreshes one market's long history per iteration. No order,
backtest/simulation only.
"""

from __future__ import annotations

import itertools

from app import config, guards, journal
from app.sweep import run_sweep

_MARKET_CYCLE = itertools.cycle(sorted(config.ALLOWED_MARKETS))

# How many distinct sliding windows the history is split into. The max reachable
# level. Grows as history grows (more data -> more independent windows).
DEFAULT_TOTAL_WINDOWS = 8


def _total_windows() -> int:
    try:
        return int(journal.get_state("total_windows", str(DEFAULT_TOTAL_WINDOWS)))
    except Exception:
        return DEFAULT_TOTAL_WINDOWS


def _refresh_one_market(bar_size: str = "1 hour", duration: str = "1 Y") -> dict:
    """Fetch ONE market's long history (rotating, pacing-tolerant)."""
    market = next(_MARKET_CYCLE)
    name = "ibkr_" + market.replace("/", "").lower() + "_long"
    try:
        from app.ibkr_data import fetch_ibkr_eurusd

        r = fetch_ibkr_eurusd(duration=duration, bar_size=bar_size, name=name, market=market)
        return {"market": market, "ok": r.get("ok", False), "bars": r.get("bars"),
                "reason": r.get("reason")}
    except Exception as exc:
        return {"market": market, "ok": False, "reason": str(exc)[:120]}


def research_iteration(markets: list[str] | None = None, refresh: bool = True) -> dict:
    """One iteration = test the NEXT window (escalate the robustness ladder)."""
    guards.assert_paper_only()
    journal.init_db()

    refresh_info = _refresh_one_market() if refresh else {"skipped": True}

    # Sweep only the rotating market each iteration: keeps runs short, spreads
    # pacing, and rotates coverage. Caller can still pin markets explicitly.
    if markets is None:
        markets = [refresh_info["market"]] if refresh_info.get("market") else None

    total = _total_windows()
    level = int(journal.get_state("iteration", "0"))
    window = (level, total)

    sweep = run_sweep(markets=markets, window=window)
    journal.set_state("iteration", str(level + 1))

    levels = journal.robustness_levels()
    proven = journal.proven_candidates()
    return {
        "iteration": level,
        "window": f"{level % total}/{total}",
        "refresh": refresh_info,
        "sweep_valid": sweep["valid"],
        "ceiling_level": levels["ceiling_level"],
        "ladder_top": levels["candidates"][:6],
        "proven_count": len(proven),
        "live": False,
    }
