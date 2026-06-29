"""High-level backtest: ParquetDataCatalog + BacktestNode (spec architecture).

This is the production-grade path the cahier des charges asks for: data lands
in a ParquetDataCatalog, the run is config-driven via BacktestNode, and the
strategy is portable. Backtest/simulation only — guards run first.
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from nautilus_trader.backtest.node import BacktestNode
from nautilus_trader.config import (
    BacktestDataConfig,
    BacktestEngineConfig,
    BacktestRunConfig,
    BacktestVenueConfig,
    ImportableStrategyConfig,
    LoggingConfig,
)
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.persistence.wranglers import BarDataWrangler
from nautilus_trader.test_kit.providers import TestInstrumentProvider

from app import config, guards
from app.data import dataset_dataframe

CATALOG_PATH = config.DATA_DIR / "catalog"


def _build_catalog(dataset: str) -> tuple[ParquetDataCatalog, object, BarType, int, str]:
    """Build (or rebuild) the catalog with the instrument + bid/ask bars."""
    if CATALOG_PATH.exists():
        shutil.rmtree(CATALOG_PATH)
    CATALOG_PATH.mkdir(parents=True, exist_ok=True)
    catalog = ParquetDataCatalog(str(CATALOG_PATH))

    instrument = TestInstrumentProvider.default_fx_ccy("EUR/USD")
    catalog.write_data([instrument])

    df_bid, provenance = dataset_dataframe(dataset)
    spread = 0.00010
    df_ask = df_bid[["open", "high", "low", "close"]] + spread
    df_ask["volume"] = df_bid["volume"]

    bid_type = BarType.from_str(f"{instrument.id}-1-MINUTE-BID-EXTERNAL")
    ask_type = BarType.from_str(f"{instrument.id}-1-MINUTE-ASK-EXTERNAL")
    bid_bars = BarDataWrangler(bid_type, instrument).process(df_bid)
    ask_bars = BarDataWrangler(ask_type, instrument).process(df_ask)
    catalog.write_data(bid_bars)
    catalog.write_data(ask_bars)
    return catalog, instrument, bid_type, len(bid_bars), provenance


def run_catalog_backtest(strategy: str = "eurusd_ema_cross", dataset: str = "realistic_eurusd") -> dict:
    """Config-driven backtest via BacktestNode over a ParquetDataCatalog."""
    guards.assert_paper_only()
    guards.scan_strategies_dir(config.STRATEGIES_DIR)
    guards.scan_text(f"{strategy} {dataset}", source="run request")
    if strategy not in config.ALLOWED_STRATEGIES:
        raise guards.LivePathBlocked(f"Strategy {strategy!r} not in allow-list.")

    catalog, instrument, bid_type, n_bars, provenance = _build_catalog(dataset)

    venue = BacktestVenueConfig(
        name="SIM",
        oms_type="NETTING",
        account_type="MARGIN",
        base_currency="USD",
        starting_balances=["1_000_000 USD"],
    )
    data = BacktestDataConfig(
        catalog_path=str(CATALOG_PATH),
        data_cls=Bar,
        instrument_id=instrument.id,
        bar_types=[str(bid_type), str(bid_type).replace("BID", "ASK")],
    )
    strat = ImportableStrategyConfig(
        strategy_path="nautilus_trader.examples.strategies.ema_cross:EMACross",
        config_path="nautilus_trader.examples.strategies.ema_cross:EMACrossConfig",
        config={
            "instrument_id": instrument.id,
            "bar_type": str(bid_type),
            "trade_size": Decimal(100_000),
            "fast_ema_period": 10,
            "slow_ema_period": 20,
        },
    )
    run = BacktestRunConfig(
        engine=BacktestEngineConfig(
            trader_id="BACKTESTER-001",
            strategies=[strat],
            logging=LoggingConfig(log_level="ERROR"),
        ),
        venues=[venue],
        data=[data],
        dispose_on_completion=False,  # keep the engine so we can export reports
    )

    node = BacktestNode(configs=[run])
    results = node.run()
    result = results[0]

    backtest_id = f"BT-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:6]}"
    out_dir = config.REPORTS_DIR / backtest_id
    out_dir.mkdir(parents=True, exist_ok=True)

    engine = node.get_engine(run.id)
    orders_df = engine.trader.generate_orders_report()
    fills_df = engine.trader.generate_fills_report()
    positions_df = engine.trader.generate_positions_report()
    orders_df.to_csv(out_dir / "orders_report.csv")
    fills_df.to_csv(out_dir / "fills_report.csv")
    positions_df.to_csv(out_dir / "positions_report.csv")
    n_orders = len(orders_df)
    n_positions = len(positions_df)

    stats = {}
    try:
        stats = {k: str(v) for k, v in result.stats_pnls.get("USD", {}).items()}
    except Exception:
        stats = {}

    summary = {
        "backtest_id": backtest_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "engine": "NautilusTrader",
        "engine_api": "BacktestNode+ParquetDataCatalog",
        "engine_version": __import__("nautilus_trader").__version__,
        "environment": config.RunnerSettings().environment,
        "strategy": strategy,
        "market": "EUR/USD",
        "dataset": dataset,
        "data_provenance": provenance,
        "bars": n_bars,
        "total_orders": int(n_orders),
        "total_positions": int(n_positions),
        "stats_pnls_usd": stats,
        "report_dir": str(out_dir),
        "live": False,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    from app import journal

    journal.init_db()
    journal.write_backtest(summary)
    return summary
