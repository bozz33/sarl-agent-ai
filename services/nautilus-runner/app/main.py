"""CLI entrypoint for nautilus-runner (backtest/simulation only).

Usage:
    python -m app.main validate-environment
    python -m app.main run-backtest --strategy eurusd_ema_cross --dataset simulated_eurusd
    python -m app.main generate-report --last
"""

from __future__ import annotations

import argparse
import json
import sys

from app import config, guards


def cmd_validate_environment() -> int:
    guards.assert_paper_only()
    scanned = guards.scan_strategies_dir(config.STRATEGIES_DIR)
    import nautilus_trader

    out = {
        "ok": True,
        "nautilus_version": nautilus_trader.__version__,
        "settings": config.RunnerSettings().as_dict(),
        "strategies_scanned": scanned,
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_run_backtest(strategy: str, dataset: str) -> int:
    # The deterministic sine series uses the low-level smoke path; everything
    # else (realistic / real CSV) uses the high-level catalog path (spec).
    if dataset == "simulated_eurusd":
        from app.runner import run_backtest

        summary = run_backtest(strategy=strategy, dataset=dataset)
    else:
        from app.catalog_runner import run_catalog_backtest

        summary = run_catalog_backtest(strategy=strategy, dataset=dataset)
    print(json.dumps(summary, indent=2))
    return 0


def cmd_generate_report(last: bool) -> int:
    dirs = sorted(config.REPORTS_DIR.glob("BT-*"))
    if not dirs:
        print(json.dumps({"error": "no backtests found"}))
        return 1
    target = dirs[-1] if last else dirs[-1]
    summary = (target / "summary.json").read_text(encoding="utf-8")
    print(summary)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nautilus-runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate-environment")

    p_run = sub.add_parser("run-backtest")
    p_run.add_argument("--strategy", default="eurusd_ema_cross")
    p_run.add_argument("--dataset", default="realistic_eurusd")

    p_wf = sub.add_parser("walk-forward")
    p_wf.add_argument("--strategy", default="eurusd_ema_atr")
    p_wf.add_argument("--dataset", default="realistic_eurusd")
    p_wf.add_argument("--folds", type=int, default=4)

    sub.add_parser("validate-ibkr")

    p_fetch = sub.add_parser("fetch-ibkr-data")
    p_fetch.add_argument("--duration", default="2 D")
    p_fetch.add_argument("--bar-size", default="1 min")
    p_fetch.add_argument("--market", default="EUR/USD")
    p_fetch.add_argument("--name", default=None)

    p_sweep = sub.add_parser("sweep")
    p_sweep.add_argument("--markets", default="")  # comma-separated; empty = all

    p_rl = sub.add_parser("research-iteration")
    p_rl.add_argument("--markets", default="")
    p_rl.add_argument("--no-refresh", action="store_true")

    p_rep = sub.add_parser("generate-report")
    p_rep.add_argument("--last", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "validate-environment":
        return cmd_validate_environment()
    if args.cmd == "run-backtest":
        return cmd_run_backtest(args.strategy, args.dataset)
    if args.cmd == "walk-forward":
        from app.walk_forward import walk_forward

        print(json.dumps(walk_forward(args.strategy, args.dataset, args.folds), indent=2))
        return 0
    if args.cmd == "validate-ibkr":
        from app.ibkr_check import check_ibkr_paper

        print(json.dumps(check_ibkr_paper(), indent=2))
        return 0
    if args.cmd == "fetch-ibkr-data":
        from app.ibkr_data import fetch_ibkr_eurusd

        print(json.dumps(fetch_ibkr_eurusd(args.duration, args.bar_size, args.name, args.market), indent=2))
        return 0
    if args.cmd == "sweep":
        from app.sweep import run_sweep

        markets = [m.strip() for m in args.markets.split(",") if m.strip()] or None
        print(json.dumps(run_sweep(markets=markets), indent=2, default=str))
        return 0
    if args.cmd == "research-iteration":
        from app.research_loop import research_iteration

        markets = [m.strip() for m in args.markets.split(",") if m.strip()] or None
        print(json.dumps(research_iteration(markets=markets, refresh=not args.no_refresh), indent=2, default=str))
        return 0
    if args.cmd == "generate-report":
        return cmd_generate_report(args.last)
    return 2


if __name__ == "__main__":
    sys.exit(main())
