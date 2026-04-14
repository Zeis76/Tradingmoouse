"""
Signal Aggregator – kombiniert alle Indikator-Signale zu einer Entscheidung.
"""
from __future__ import annotations

import logging
import pandas as pd

from strategy.decision import Decision, SignalType
from indicators.trend import TrendIndicators

logger = logging.getLogger(__name__)


class SignalAggregator:

    def __init__(self, config: dict, scalping_mode: bool = False) -> None:
        self.scalping_mode = scalping_mode
        indicator_cfg = config.get("indicators", {})
        self.weights: dict[str, float] = config.get("signal_weights", {
            "macd":         0.15,
            "ema_cross":    0.12,
        })
        self.min_score: float = config.get("trading", {}).get("min_signal_score", 0.65)

        # Indikator-Instanzen
        self.trend = TrendIndicators(indicator_cfg.get("ema", {}))

    def analyze(
        self,
        df: pd.DataFrame,
        symbol: str,
        exchange: str,
        timeframe: str,
    ) -> Decision:
        """Kombiniert Signale zu einer Entscheidung."""
        
        results = {
            "macd":         self.trend.macd(df),
            "ema_cross":    self.trend.ema_cross(df),
        }

        weighted_sum = 0.0
        weight_used = 0.0
        raw_scores = {}

        for name, result in results.items():
            if result.value is None: continue
            weight = self.weights.get(name, 0.0)
            raw_scores[name] = result.signal
            weighted_sum += result.signal * weight
            weight_used += weight

        final_score = weighted_sum / weight_used if weight_used > 0 else 0.0
        
        abs_score = abs(final_score)
        if abs_score >= self.min_score:
            signal = SignalType.BUY if final_score > 0 else SignalType.SELL
            direction = "long" if final_score > 0 else "short"
        else:
            signal = SignalType.HOLD
            direction = "none"

        return Decision(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            signal=signal,
            score=round(final_score, 4),
            confidence=0.5,
            direction=direction,
            indicator_scores=raw_scores
        )
