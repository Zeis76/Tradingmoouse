"""
Trend-Indikatoren: EMA, SMA, MACD, ADX.
"""
from __future__ import annotations

import pandas as pd
import ta.trend as tat

from .base import BaseIndicator, IndicatorResult


class TrendIndicators(BaseIndicator):

    def __init__(self, config: dict) -> None:
        self.ema_short  = config.get("short", 9)
        self.ema_medium = config.get("medium", 21)
        self.ema_long   = config.get("long", 50)
        self.macd_fast   = 12
        self.macd_slow   = 26
        self.macd_signal = 9

    def ema_cross(self, df: pd.DataFrame) -> IndicatorResult:
        if not self._validate(df, self.ema_long + 5):
            return IndicatorResult("ema_cross", 0.0, None)
        try:
            close = df["close"]
            ema_s = tat.EMAIndicator(close, window=self.ema_short).ema_indicator()
            ema_m = tat.EMAIndicator(close, window=self.ema_medium).ema_indicator()
            ema_l = tat.EMAIndicator(close, window=self.ema_long).ema_indicator()

            s, m, l_ = ema_s.iloc[-1], ema_m.iloc[-1], ema_l.iloc[-1]
            s_prev, m_prev = ema_s.iloc[-2], ema_m.iloc[-2]

            above_long      = close.iloc[-1] > l_
            cross_up        = s > m and s_prev <= m_prev
            cross_down      = s < m and s_prev >= m_prev
            short_above_med = s > m

            if cross_up:
                score = 0.9
            elif cross_down:
                score = -0.9
            elif short_above_med and above_long:
                score = 0.5
            elif not short_above_med and not above_long:
                score = -0.5
            else:
                score = 0.2 if short_above_med else -0.2

            return IndicatorResult(
                "ema_cross", signal=score, value=float(s - m),
                metadata={"ema_short": float(s), "ema_medium": float(m), "ema_long": float(l_)},
            )
        except Exception:
            return IndicatorResult("ema_cross", 0.0, None)

    def macd(self, df: pd.DataFrame) -> IndicatorResult:
        if not self._validate(df, self.macd_slow + self.macd_signal + 5):
            return IndicatorResult("macd", 0.0, None)
        try:
            macd_ind = tat.MACD(
                df["close"],
                window_slow=self.macd_slow,
                window_fast=self.macd_fast,
                window_sign=self.macd_signal,
            )
            hist = macd_ind.macd_diff()
            h_now  = hist.iloc[-1]
            h_prev = hist.iloc[-2]

            growing   = h_now > h_prev
            cross_up   = h_now > 0 and h_prev <= 0
            cross_down = h_now < 0 and h_prev >= 0

            if cross_up:            score = 0.9
            elif cross_down:        score = -0.9
            elif h_now > 0 and growing:   score = 0.7
            elif h_now > 0:               score = 0.2
            elif h_now < 0 and not growing: score = -0.7
            else:                         score = -0.2

            return IndicatorResult(
                "macd", signal=score, value=float(h_now),
                metadata={"histogram": float(h_now), "histogram_prev": float(h_prev)},
            )
        except Exception:
            return IndicatorResult("macd", 0.0, None)

    def adx(self, df: pd.DataFrame, period: int = 14) -> IndicatorResult:
        if not self._validate(df, period * 2):
            return IndicatorResult("adx", 0.0, None)
        try:
            adx_ind = tat.ADXIndicator(df["high"], df["low"], df["close"], window=period)
            adx_val = adx_ind.adx().iloc[-1]
            dmp     = adx_ind.adx_pos().iloc[-1]
            dmn     = adx_ind.adx_neg().iloc[-1]

            strength = min(adx_val / 50.0, 1.0)
            direction_score = strength if dmp > dmn else (-strength if dmn > dmp else 0.0)

            return IndicatorResult(
                "adx", signal=direction_score, value=float(adx_val),
                metadata={"adx": float(adx_val), "dmp": float(dmp), "dmn": float(dmn)},
            )
        except Exception:
            return IndicatorResult("adx", 0.0, None)
