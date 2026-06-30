"""Autonomous research loop — find strategies that are PROVEN over many runs.

One iteration:
  1. Try to refresh ONE market's long history from IBKR (pacing-safe: a single
     request; rotates markets so the loop self-throttles over time).
  2. Run the multi-family / multi-timeframe sweep (walk-forward each shortlist).
  3. Each walk-forwarded config is upserted into strategy_candidates, so a
     config's robustness is accumulated across iterations, not judged once.
  4. A candidate becomes "proven" only after surviving walk-forward repeatedly
     (journal.PROVEN_MIN_ROBUST times, >= PROVEN_MIN_RATIO survival ratio).

Designed to run on a schedule (cron). No order, backtest/simulation only.
"""

from __future__ import annotations

import itertools

from app import config, guards, journal
from app.sweep import run_sweep

# Rotate which market we try to refresh each iteration (self-throttle pacing).
_MARKET_CYCLE = itertools.cycle(sorted(config.ALLOWED_MARKETS))


def _refresh_one_market(bar_size: str = "1 hour", duration: str = "1 Y") -> dict:
    """Fetch ONE market's long history (rotating). Tolerates pacing failures."""
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
    """One autonomous research iteration. Returns proven candidates so far."""
    guards.assert_paper_only()
    refresh_info = _refresh_one_market() if refresh else {"skipped": True}

    sweep = run_sweep(markets=markets)  # upserts candidates via walk-forward

    proven = journal.proven_candidates()
    return {
        "refresh": refresh_info,
        "sweep_ran": sweep["ran"],
        "sweep_valid": sweep["valid"],
        "by_timeframe": sweep.get("by_timeframe", {}),
        "iteration_best": sweep.get("best"),
        "proven_count": len(proven),
        "proven": proven[:10],
        "live": False,
    }
