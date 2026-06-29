"""Backtest runner: the only path Hermes uses to run NautilusTrader.

v1: low-level BacktestEngine, EUR/USD, EMA cross, synthetic bars, SIM venue.
No TradingNode, no LiveNode, no broker. Guards run before anything else.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model.data import BarType
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.persistence.wranglers import BarDataWrangler
from nautilus_trader.test_kit.providers import TestInstrumentProvider

from app import config, guards
from app.data import synthetic_eurusd_bars
from strategies.eurusd_ema_cross import EMACross, EMACrossConfig


def run_backtest(strategy: str = "eurusd_ema_cross", dataset: str = "simulated_eurusd") -> dict:
    """Run the allow-listed backtest and return a summary dict.

    Refuses anything outside the v1 allow-list and any live path.
    """
    # 1. Hard guards first — fail closed.
    guards.assert_paper_only()
    guards.scan_strategies_dir(config.STRATEGIES_DIR)
    guards.scan_text(f"{strategy} {dataset}", source="run request")
    if strategy not in config.ALLOWED_STRATEGIES:
        raise guards.LivePathBlocked(f"Strategy {strategy!r} not in allow-list.")

    # 2. Engine (backtest only).
    engine = BacktestEngine(
        config=BacktestEngineConfig(
            trader_id="BACKTESTER-001",
            logging=LoggingConfig(log_level="ERROR"),
        )
    )

    # 3. Simulated FX venue + EUR/USD instrument.
    venue = Venue("SIM")
    engine.add_venue(
        venue=venue,
        oms_type=OmsType.NETTING,
        account_type=AccountType.MARGIN,
        base_currency=USD,
        starting_balances=[Money(1_000_000, USD)],
    )
    instrument = TestInstrumentProvider.default_fx_ccy("EUR/USD", venue=venue)
    engine.add_instrument(instrument)

    # 4. Synthetic bars -> Nautilus Bar objects. The matching engine needs
    # both BID and ASK to build an L1 book and fill FX market orders, so we
    # feed two series (ASK = BID + spread). The strategy subscribes to BID.
    spread = 0.00010
    df_bid = synthetic_eurusd_bars()
    df_ask = df_bid[["open", "high", "low", "close"]] + spread
    df_ask["volume"] = df_bid["volume"]

    bar_type = BarType.from_str(f"{instrument.id}-1-MINUTE-BID-EXTERNAL")
    ask_bar_type = BarType.from_str(f"{instrument.id}-1-MINUTE-ASK-EXTERNAL")
    bid_bars = BarDataWrangler(bar_type, instrument).process(df_bid)
    ask_bars = BarDataWrangler(ask_bar_type, instrument).process(df_ask)
    bars = bid_bars
    engine.add_data(bid_bars)
    engine.add_data(ask_bars)

    # 5. Strategy.
    strat = EMACross(
        config=EMACrossConfig(
            instrument_id=instrument.id,
            bar_type=bar_type,
            trade_size=Decimal(100_000),
            fast_ema_period=10,
            slow_ema_period=20,
        )
    )
    engine.add_strategy(strat)

    # 6. Run + collect.
    engine.run()
    result = engine.get_result()

    backtest_id = f"BT-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:6]}"
    out_dir = config.REPORTS_DIR / backtest_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # CSV reports.
    engine.trader.generate_orders_report().to_csv(out_dir / "orders_report.csv")
    engine.trader.generate_fills_report().to_csv(out_dir / "fills_report.csv")
    engine.trader.generate_positions_report().to_csv(out_dir / "positions_report.csv")
    engine.trader.generate_account_report(venue).to_csv(out_dir / "account_report.csv")

    stats = {}
    try:
        stats = {k: str(v) for k, v in result.stats_pnls.get("USD", {}).items()}
    except Exception:
        stats = {}

    summary = {
        "backtest_id": backtest_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "engine": "NautilusTrader",
        "engine_version": __import__("nautilus_trader").__version__,
        "environment": config.RunnerSettings().environment,
        "strategy": strategy,
        "market": "EUR/USD",
        "dataset": dataset,
        "bars": len(bars),
        "total_orders": int(result.total_orders),
        "total_positions": int(result.total_positions),
        "stats_pnls_usd": stats,
        "report_dir": str(out_dir),
        "live": False,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
