"""Bounded trading missions. NO infinite loop.

Each mission is deterministic, runs once, produces an artifact, and returns.
A cron / SARL scheduler invokes these; they never loop forever and never
change a rule on their own.
"""

from __future__ import annotations

from app import guards, reports


def daily_cycle(strategy: str = "eurusd_ema_cross", dataset: str = "realistic_eurusd") -> dict:
    """One bounded daily mission: validate -> backtest -> journal -> daily report."""
    guards.assert_paper_only()
    if dataset == "simulated_eurusd":
        from app.runner import run_backtest

        summary = run_backtest(strategy=strategy, dataset=dataset)  # writes journal
    else:
        from app.catalog_runner import run_catalog_backtest

        summary = run_catalog_backtest(strategy=strategy, dataset=dataset)  # writes journal
    report = reports.daily_report()
    return {
        "mission": "daily_trading_demo",
        "backtest_id": summary["backtest_id"],
        "report_chars": len(report),
        "live": False,
    }


def weekly_review() -> dict:
    """One bounded weekly mission: produce the weekly learning review."""
    guards.assert_paper_only()
    report = reports.weekly_report()
    return {"mission": "weekly_trading_review", "report_chars": len(report), "live": False}


MISSIONS = {
    "daily_trading_demo": daily_cycle,
    "weekly_trading_review": weekly_review,
}


def run_mission(name: str) -> dict:
    if name not in MISSIONS:
        raise ValueError(f"unknown mission {name!r}; allowed: {sorted(MISSIONS)}")
    return MISSIONS[name]()


if __name__ == "__main__":
    import json
    import sys

    name = sys.argv[1] if len(sys.argv) > 1 else "daily_trading_demo"
    print(json.dumps(run_mission(name), indent=2))
