"""Research sweep — fast learning by batch backtesting.

Backtesting is offline and instant, so instead of one backtest per day we run a
whole matrix of (market x strategy x parameter set) at once, rank them, and
walk-forward the best for robustness. Dozens of lessons in minutes, not weeks.
All backtest/simulation, no order.
"""

from __future__ import annotations

import itertools
from datetime import datetime, timezone

from app import config, guards, journal
from app.catalog_runner import run_catalog_backtest
from app.walk_forward import walk_forward


def _grid() -> list[tuple[str, dict]]:
    """Bounded (strategy, params) grid."""
    combos: list[tuple[str, dict]] = []
    # Naive EMA cross: fast/slow only.
    for fast, slow in itertools.product((8, 12), (20, 50)):
        combos.append(("eurusd_ema_cross", {"fast_ema_period": fast, "slow_ema_period": slow}))
    # Enriched EMA+RSI+ATR: fast/slow + ATR stop + R:R.
    for fast, slow, atr_mult, rr in itertools.product((8, 12), (20, 50), (1.5, 2.5), (1.5, 2.0)):
        combos.append(("eurusd_ema_atr", {
            "fast_ema_period": fast, "slow_ema_period": slow,
            "atr_stop_mult": atr_mult, "rr": rr,
        }))
    return combos


def _num(stats: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(stats.get(key, default))
    except Exception:
        return default


def run_sweep(markets: list[str] | None = None, max_combos: int = 80,
              min_positions: int = 8, top_n: int = 3,
              timeframes: list[str | None] | None = None) -> dict:
    """Backtest the grid across markets x timeframes, rank, walk-forward top, journal."""
    guards.assert_paper_only()
    markets = markets or sorted(config.ALLOWED_MARKETS)
    # None = native 1-min; others resample to cut intraday noise.
    timeframes = timeframes if timeframes is not None else [None, "15min", "1h"]
    grid = _grid()[:max_combos]

    rows = []
    for market in markets:
        dataset = "ibkr_" + market.replace("/", "").lower()  # real CSV if present, else realistic
        for tf in timeframes:
            for strategy, params in grid:
                try:
                    s = run_catalog_backtest(strategy=strategy, dataset=dataset, market=market,
                                             params_override=params, record=False, resample=tf)
                except Exception as exc:
                    rows.append({"market": market, "timeframe": tf or "1min", "strategy": strategy,
                                 "params": params, "error": str(exc)[:120]})
                    continue
                st = s["stats_pnls_usd"]
                rows.append({
                    "market": market,
                    "timeframe": tf or "1min",
                    "_tf": tf,
                    "strategy": strategy,
                    "params": params,
                    "provenance": s["data_provenance"],
                    "positions": s["total_positions"],
                    "pnl": _num(st, "PnL (total)"),
                    "win_rate": _num(st, "Win Rate"),
                    "expectancy": _num(st, "Expectancy"),
                })

    # Rank: enough trades to be meaningful, then by PnL, then win rate.
    valid = [r for r in rows if "error" not in r and r["positions"] >= min_positions]
    valid.sort(key=lambda r: (r["pnl"], r["win_rate"]), reverse=True)
    top = valid[:top_n]

    # Walk-forward the best ones for out-of-sample robustness (same timeframe).
    for r in top:
        try:
            wf = walk_forward(strategy=r["strategy"],
                              dataset="ibkr_" + r["market"].replace("/", "").lower(),
                              folds=4, market=r["market"], params_override=r["params"],
                              resample=r.get("_tf"))
            r["walk_forward"] = wf["aggregate"]
        except Exception as exc:
            r["walk_forward"] = {"error": str(exc)[:120]}

    # Per-timeframe aggregate (the headline finding: does a larger TF help?).
    by_tf = {}
    for tf in {r["timeframe"] for r in valid}:
        sub = [r for r in valid if r["timeframe"] == tf]
        by_tf[tf] = {
            "configs": len(sub),
            "profitable": sum(1 for r in sub if r["pnl"] > 0),
            "mean_pnl": round(sum(r["pnl"] for r in sub) / len(sub), 1),
            "mean_win_rate": round(sum(r["win_rate"] for r in sub) / len(sub), 3),
        }

    best = top[0] if top else None
    # Journal the sweep as a learning artifact.
    if best:
        lesson = (f"Sweep {datetime.now(timezone.utc):%Y-%m-%d}: best = {best['strategy']} "
                  f"on {best['market']} {best['timeframe']} params={best['params']} "
                  f"PnL={best['pnl']} WR={round(best['win_rate'],3)} WF={best.get('walk_forward')}. "
                  f"Per-timeframe: {by_tf}. Tested {len(valid)}/{len(rows)} valid configs.")
        journal.init_db()
        journal.write_learning_proposal(lesson)

    return {
        "ran": len(rows),
        "valid": len(valid),
        "markets": markets,
        "timeframes": [tf or "1min" for tf in timeframes],
        "by_timeframe": by_tf,
        "top": top,
        "best": best,
        "live": False,
    }
