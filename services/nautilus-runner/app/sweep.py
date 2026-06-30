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
    """Bounded (strategy, params) grid across families: trend, MR, breakout."""
    combos: list[tuple[str, dict]] = []
    # Trend: naive EMA cross.
    for fast, slow in itertools.product((8, 12), (20, 50)):
        combos.append(("eurusd_ema_cross", {"fast_ema_period": fast, "slow_ema_period": slow}))
    # Trend: enriched EMA+RSI+ATR.
    for fast, slow, atr_mult, rr in itertools.product((8, 12), (20, 50), (1.5, 2.5), (1.5, 2.0)):
        combos.append(("eurusd_ema_atr", {
            "fast_ema_period": fast, "slow_ema_period": slow,
            "atr_stop_mult": atr_mult, "rr": rr,
        }))
    # Mean-reversion: Bollinger fade, range-filtered.
    for bb_k, er_max, atr_mult in itertools.product((1.5, 2.0), (0.3, 0.4), (1.5, 2.5)):
        combos.append(("bollinger_mr", {"bb_k": bb_k, "er_range_max": er_max, "atr_stop_mult": atr_mult}))
    # Breakout: Donchian, trend-filtered.
    for dc, er_min, rr in itertools.product((20, 40), (0.35, 0.5), (1.5, 2.5)):
        combos.append(("donchian_break", {"dc_period": dc, "er_trend_min": er_min, "rr": rr}))
    return combos


def _num(stats: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(stats.get(key, default))
    except Exception:
        return default


def _resolve_market_data(market: str) -> tuple[str, list[str | None]]:
    """Pick the best dataset + sensible timeframes for a market.

    Prefer long history (1h native, ~1y) -> test 1h + 4h + 1D aggregates.
    Else short 1-min -> test 1min + 15min + 1h. Else realistic generator.
    """
    from app.data import HISTORICAL_DIR

    slug = market.replace("/", "").lower()
    if (HISTORICAL_DIR / f"ibkr_{slug}_long.csv").exists():
        return f"ibkr_{slug}_long", [None, "4h", "1D"]
    if (HISTORICAL_DIR / f"ibkr_{slug}.csv").exists():
        return f"ibkr_{slug}", [None, "15min", "1h"]
    return "realistic", [None, "15min", "1h"]


def run_sweep(markets: list[str] | None = None, max_combos: int = 120,
              min_positions: int = 5, top_n: int = 3,
              timeframes: list[str | None] | None = None,
              window: tuple[int, int] | None = None) -> dict:
    """Backtest the grid across markets x timeframes, rank, walk-forward top, journal."""
    guards.assert_paper_only()
    journal.init_db()  # ensure strategy_candidates exists before upserts
    markets = markets or sorted(config.ALLOWED_MARKETS)
    grid = _grid()[:max_combos]

    rows = []
    for market in markets:
        dataset, auto_tfs = _resolve_market_data(market)
        tfs = timeframes if timeframes is not None else auto_tfs
        for tf in tfs:
            for strategy, params in grid:
                try:
                    s = run_catalog_backtest(strategy=strategy, dataset=dataset, market=market,
                                             params_override=params, record=False, resample=tf, window=window)
                except Exception as exc:
                    rows.append({"market": market, "timeframe": tf or "1min", "strategy": strategy,
                                 "params": params, "error": str(exc)[:120]})
                    continue
                st = s["stats_pnls_usd"]
                rows.append({
                    "market": market,
                    "dataset": dataset,
                    "timeframe": tf or "native",
                    "_tf": tf,
                    "strategy": strategy,
                    "params": params,
                    "provenance": s["data_provenance"],
                    "positions": s["total_positions"],
                    "pnl": _num(st, "PnL (total)"),
                    "win_rate": _num(st, "Win Rate"),
                    "expectancy": _num(st, "Expectancy"),
                })

    # Rank by EXPECTANCY (per-trade edge — fairer than raw PnL across sample
    # sizes), requiring enough trades to be meaningful. The 2025-26 literature
    # favours expectancy + robustness over raw PnL / win rate.
    valid = [r for r in rows if "error" not in r and r["positions"] >= min_positions]
    valid.sort(key=lambda r: (r["expectancy"], r["pnl"]), reverse=True)
    # Walk-forward a wider shortlist, then keep only out-of-sample-robust ones.
    shortlist = valid[: max(top_n * 3, 6)]
    for r in shortlist:
        try:
            wf = walk_forward(strategy=r["strategy"],
                              dataset=r.get("dataset", "ibkr_" + r["market"].replace("/", "").lower()),
                              folds=4, market=r["market"], params_override=r["params"],
                              resample=r.get("_tf"), window=window)
            r["walk_forward"] = wf["aggregate"]
            agg = wf["aggregate"]
            # Robust score: reward OOS consistency + OOS mean PnL, penalise variance.
            prof = agg.get("profitable_folds", "0/4")
            folds_ok = int(str(prof).split("/")[0]) if "/" in str(prof) else 0
            r["robust_score"] = round(folds_ok + agg.get("mean_pnl", 0.0) / 1000.0
                                      - agg.get("pnl_stdev", 0.0) / 2000.0, 3)
            # Record the candidate so its robustness is judged over MANY runs.
            try:
                obs = journal.upsert_candidate(
                    r["strategy"], r["market"], r["timeframe"], r["params"],
                    is_robust=bool(agg.get("consistent")), robust_score=r["robust_score"])
                r["candidate"] = obs
            except Exception:
                pass
        except Exception as exc:
            r["walk_forward"] = {"error": str(exc)[:120]}
            r["robust_score"] = -999.0

    # Final ranking = robustness first.
    shortlist.sort(key=lambda r: r.get("robust_score", -999.0), reverse=True)
    top = shortlist[:top_n]

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
        "timeframes": sorted({r["timeframe"] for r in valid}) if valid else [],
        "by_timeframe": by_tf,
        "top": top,
        "best": best,
        "live": False,
    }
