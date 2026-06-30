"""Bollinger mean-reversion with a range-regime filter (backtest only).

Mean-reversion family for RANGING markets: fade extremes back to the mean.
- Bollinger Bands  -> entry when price pierces a band
- RSI              -> confirm extreme (oversold buy / overbought sell)
- EfficiencyRatio  -> regime filter: only trade when ER is LOW (range, not trend)
- ATR              -> stop, exit back at the middle band (mean)

No live path. Allow-listed under id `bollinger_mr`.
"""

from __future__ import annotations

from decimal import Decimal

from nautilus_trader.indicators import (
    AverageTrueRange,
    BollingerBands,
    EfficiencyRatio,
    RelativeStrengthIndex,
)
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.trading.strategy import Strategy, StrategyConfig


class BollingerMrConfig(StrategyConfig, frozen=True):
    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    bb_period: int = 20
    bb_k: float = 2.0
    rsi_period: int = 14
    er_period: int = 10
    atr_period: int = 14
    rsi_oversold: float = 35.0
    rsi_overbought: float = 65.0
    er_range_max: float = 0.35  # only trade when EfficiencyRatio <= this (range)
    atr_stop_mult: float = 2.0


class BollingerMr(Strategy):
    def __init__(self, config: BollingerMrConfig) -> None:
        super().__init__(config)
        self.bb = BollingerBands(config.bb_period, config.bb_k)
        self.rsi = RelativeStrengthIndex(config.rsi_period)
        self.er = EfficiencyRatio(config.er_period)
        self.atr = AverageTrueRange(config.atr_period)
        self.instrument = None
        self._sl = None

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        for ind in (self.bb, self.rsi, self.er, self.atr):
            self.register_indicator_for_bars(self.config.bar_type, ind)
        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        if not (self.bb.initialized and self.rsi.initialized and self.er.initialized and self.atr.initialized):
            return
        px = float(bar.close)
        iid = self.config.instrument_id

        # Manage open position: stop, or take profit at the mean (middle band).
        if not self.portfolio.is_flat(iid):
            long = self.portfolio.is_net_long(iid)
            hit_stop = (px <= self._sl) if long else (px >= self._sl)
            hit_mean = (px >= self.bb.middle) if long else (px <= self.bb.middle)
            if hit_stop or hit_mean:
                self.close_all_positions(iid)
                self._sl = None
            return

        # Regime filter: only fade in a range (low efficiency).
        if self.er.value > self.config.er_range_max:
            return

        dist = self.config.atr_stop_mult * self.atr.value
        if px <= self.bb.lower and self.rsi.value < self.config.rsi_oversold:
            self._enter(OrderSide.BUY, px - dist)
        elif px >= self.bb.upper and self.rsi.value > self.config.rsi_overbought:
            self._enter(OrderSide.SELL, px + dist)

    def _enter(self, side: OrderSide, stop: float) -> None:
        order = self.order_factory.market(
            instrument_id=self.config.instrument_id,
            order_side=side,
            quantity=self.instrument.make_qty(self.config.trade_size),
            time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)
        self._sl = stop

    def on_stop(self) -> None:
        self.close_all_positions(self.config.instrument_id)
