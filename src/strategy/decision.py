"""
Entscheidungs-Datenklassen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Decision:
    """Finale Handelsentscheidung für ein Symbol."""
    symbol: str
    exchange: str
    timeframe: str
    signal: SignalType
    score: float
    confidence: float
    direction: str
    indicator_scores: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_actionable(self) -> bool:
        return self.signal != SignalType.HOLD

    @property
    def summary(self) -> str:
        scores_str = " | ".join(
            f"{k}={v:+.2f}" for k, v in self.indicator_scores.items()
        )
        return (
            f"{self.symbol} -> {self.signal.upper()} "
            f"score={self.score:+.3f} conf={self.confidence:.0%}"
        )
