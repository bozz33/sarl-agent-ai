"""Walk-forward validation.

Splits the dataset into sequential out-of-sample folds and backtests the
(fixed-parameter) strategy on each. A strategy that only works on one period
collapses here; a robust one stays consistent across folds. Defends against
overfitting / curve-fitting. Backtest/simulation only.
"""

from __future__ import annotations

from statistics import mean, pstdev

from app import config, guards
from app.catalog_runner import run_catalog_backtest
from app.data import dataset_dataframe


def _pnl(summary: dict) -> float:
    try:
        return float(summary["stats_pnls_usd"].get("PnL (total)", 0.0))
    except Exception:
        return 0.0


def _win_rate(summary: dict) -> float:
    try:
        return float(summary["stats_pnls_usd"].get("Win Rate", 0.0))
    except Exception:
        return 0.0


def walk_forward(strategy: str = "eurusd_ema_atr", dataset: str = "realistic_eurusd", folds: int = 4) -> dict:
    """Run the strategy on `folds` sequential out-of-sample slices."""
    guards.assert_paper_only()
    if strategy not in config.ALLOWED_STRATEGIES:
        raise guards.LivePathBlocked(f"Strategy {strategy!r} not in allow-list.")
    if folds < 2:
        raise ValueError("walk_forward needs at least 2 folds")

    df, provenance = dataset_dataframe(dataset)
    n = len(df)
    size = n // folds
    fold_results = []
    for i in range(folds):
        start = i * size
        end = n if i == folds - 1 else (i + 1) * size
        slice_df = df.iloc[start:end]
        s = run_catalog_backtest(strategy=strategy, dataset=dataset, df=slice_df, record=False)
        fold_results.append({
            "fold": i + 1,
            "bars": int(s["bars"]),
            "positions": int(s["total_positions"]),
            "pnl": _pnl(s),
            "win_rate": _win_rate(s),
        })

    pnls = [f["pnl"] for f in fold_results]
    wrs = [f["win_rate"] for f in fold_results if f["positions"] > 0]
    profitable = sum(1 for p in pnls if p > 0)
    return {
        "strategy": strategy,
        "dataset": dataset,
        "data_provenance": provenance,
        "folds": folds,
        "fold_results": fold_results,
        "aggregate": {
            "mean_pnl": round(mean(pnls), 2),
            "pnl_stdev": round(pstdev(pnls), 2) if len(pnls) > 1 else 0.0,
            "mean_win_rate": round(mean(wrs), 4) if wrs else 0.0,
            "profitable_folds": f"{profitable}/{folds}",
            "consistent": profitable >= folds - 1,  # robust if all-but-one folds profitable
        },
        "live": False,
    }
