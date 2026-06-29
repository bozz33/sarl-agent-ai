"""EUR/USD EMA trend + RSI filter + ATR stops/no-trade (v2, backtest only).

Adds signal-quality filters over the naive EMA cross:
- EMA fast/slow  -> trend direction
- RSI            -> skip entries in overbought/oversold extremes
- ATR            -> no-trade gate on extreme volatility + ATR-based stop/target

No live path. Allow-listed under id `eurusd_ema_atr`.
"""

from __future__ import annotations

from decimal import Decimal

from nautilus_trader.indicators import (
    AverageTrueRange,
    ExponentialMovingAverage,
    RelativeStrengthIndex,
)
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.trading.strategy import Strategy, StrategyConfig


class EmaAtrConfig(StrategyConfig, frozen=True):
    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    fast_ema_period: int = 10
    slow_ema_period: int = 20
    rsi_period: int = 14
    atr_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0
    atr_no_trade: float = 0.0025  # price units; skip entries above this ATR
    atr_stop_mult: float = 2.0
    rr: float = 1.5


class EmaAtr(Strategy):
    def __init__(self, config: EmaAtrConfig) -> None:
        super().__init__(config)
        self.fast = ExponentialMovingAverage(config.fast_ema_period)
        self.slow = ExponentialMovingAverage(config.slow_ema_period)
        self.rsi = RelativeStrengthIndex(config.rsi_period)
        self.atr = AverageTrueRange(config.atr_period)
        self.instrument = None
        self._sl = None
        self._tp = None

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        for ind in (self.fast, self.slow, self.rsi, self.atr):
            self.register_indicator_for_bars(self.config.bar_type, ind)
        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        if not (self.fast.initialized and self.slow.initialized and self.rsi.initialized and self.atr.initialized):
            return
        px = float(bar.close)
        atr = self.atr.value
        iid = self.config.instrument_id

        # Manage an open position: ATR stop / target.
        if not self.portfolio.is_flat(iid):
            if self._sl is not None:
                long = self.portfolio.is_net_long(iid)
                hit_stop = (px <= self._sl) if long else (px >= self._sl)
                hit_target = (px >= self._tp) if long else (px <= self._tp)
                if hit_stop or hit_target:
                    self.close_all_positions(iid)
                    self._sl = self._tp = None
            return

        # Flat: no-trade gate on extreme volatility.
        if atr > self.config.atr_no_trade:
            return

        # Entry with trend + RSI filters.
        if self.fast.value > self.slow.value and self.rsi.value < self.config.rsi_overbought:
            self._enter(OrderSide.BUY, px, atr)
        elif self.fast.value < self.slow.value and self.rsi.value > self.config.rsi_oversold:
            self._enter(OrderSide.SELL, px, atr)

    def _enter(self, side: OrderSide, px: float, atr: float) -> None:
        order = self.order_factory.market(
            instrument_id=self.config.instrument_id,
            order_side=side,
            quantity=self.instrument.make_qty(self.config.trade_size),
            time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)
        dist = self.config.atr_stop_mult * atr
        if side == OrderSide.BUY:
            self._sl, self._tp = px - dist, px + self.config.rr * dist
        else:
            self._sl, self._tp = px + dist, px - self.config.rr * dist

    def on_stop(self) -> None:
        self.close_all_positions(self.config.instrument_id)
