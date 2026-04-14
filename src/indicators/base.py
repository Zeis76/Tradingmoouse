"""
Basis-Klasse für alle Indikatoren.
Jeder Indikator gibt ein normiertes Signal zurück:
  -1.0 = Starkes SELL
   0.0 = Neutral
  +1.0 = Starkes BUY
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class IndicatorResult:
    """Ergebnis eines einzelnen Indikators."""
    name: str
    signal: float          # -1.0 bis +1.0
    value: float | None    # Rohwert des Indikators
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.signal = max(-1.0, min(1.0, self.signal))

    @property
    def direction(self) -> str:
        if self.signal > 0.3:
            return "BUY"
        if self.signal < -0.3:
            return "SELL"
        return "NEUTRAL"


class BaseIndicator:
    """Basisklasse – stellt Hilfsmethoden bereit."""

    @staticmethod
    def _validate(df: pd.DataFrame, min_rows: int = 30) -> bool:
        return isinstance(df, pd.DataFrame) and len(df) >= min_rows

    @staticmethod
    def _normalize(value: float, low: float, high: float) -> float:
        """Normiert einen Wert auf [-1, 1] relativ zu low/high."""
        if high == low:
            return 0.0
        mid = (high + low) / 2
        return max(-1.0, min(1.0, (value - mid) / ((high - low) / 2)))
