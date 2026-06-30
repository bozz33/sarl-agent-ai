"""Donchian breakout with a trend-regime filter (backtest only).

Trend-following family for TRENDING markets: ride breakouts of the N-bar range.
- DonchianChannel  -> entry on a break of the upper/lower channel
- EfficiencyRatio  -> regime filter: only trade when ER is HIGH (trend, not range)
- ATR              -> stop and ATR-based target

No live path. Allow-listed under id `donchian_break`.
"""

from __future__ import annotations

from decimal import Decimal

from nautilus_trader.indicators import (
    AverageTrueRange,
    DonchianChannel,
    EfficiencyRatio,
)
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.trading.strategy import Strategy, StrategyConfig


class DonchianBreakConfig(StrategyConfig, frozen=True):
    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    dc_period: int = 20
    er_period: int = 10
    atr_period: int = 14
    er_trend_min: float = 0.4  # only trade when EfficiencyRatio >= this (trend)
    atr_stop_mult: float = 2.0
    rr: float = 2.0


class DonchianBreak(Strategy):
    def __init__(self, config: DonchianBreakConfig) -> None:
        super().__init__(config)
        self.dc = DonchianChannel(config.dc_period)
        self.er = EfficiencyRatio(config.er_period)
        self.atr = AverageTrueRange(config.atr_period)
        self.instrument = None
        self._sl = None
        self._tp = None

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        for ind in (self.dc, self.er, self.atr):
            self.register_indicator_for_bars(self.config.bar_type, ind)
        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        if not (self.dc.initialized and self.er.initialized and self.atr.initialized):
            return
        px = float(bar.close)
        iid = self.config.instrument_id

        if not self.portfolio.is_flat(iid):
            long = self.portfolio.is_net_long(iid)
            hit_stop = (px <= self._sl) if long else (px >= self._sl)
            hit_tp = (px >= self._tp) if long else (px <= self._tp)
            if hit_stop or hit_tp:
                self.close_all_positions(iid)
                self._sl = self._tp = None
            return

        # Regime filter: only break out in a trend (high efficiency).
        if self.er.value < self.config.er_trend_min:
            return

        dist = self.config.atr_stop_mult * self.atr.value
        if px >= self.dc.upper:
            self._enter(OrderSide.BUY, px - dist, px + self.config.rr * dist)
        elif px <= self.dc.lower:
            self._enter(OrderSide.SELL, px + dist, px - self.config.rr * dist)

    def _enter(self, side: OrderSide, stop: float, target: float) -> None:
        order = self.order_factory.market(
            instrument_id=self.config.instrument_id,
            order_side=side,
            quantity=self.instrument.make_qty(self.config.trade_size),
            time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)
        self._sl, self._tp = stop, target

    def on_stop(self) -> None:
        self.close_all_positions(self.config.instrument_id)
