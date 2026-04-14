import logging
import os
from typing import Any

import ccxt.async_support as ccxt
import pandas as pd

logger = logging.getLogger(__name__)


class ExchangeWrapper:
    """Wrapper um CCXT für einheitlichen Zugriff auf Exchanges."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.exchange_id = "binance"
        self.exchange: ccxt.Exchange | None = None
        self.name = "Binance"

    async def initialize(self) -> None:
        """Initialisiert die Verbindung zur Exchange."""
        api_key = os.getenv("BINANCE_API_KEY", "")
        api_secret = os.getenv("BINANCE_API_SECRET", "")

        is_demo = self.config.get("bot", {}).get("demo", True)

        self.exchange = ccxt.binance({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"}
        })

        if is_demo:
            self.exchange.set_sandbox_mode(True)
            logger.info("Binance TESTNET aktiv.")

        markets = await self.exchange.load_markets()
        logger.info(f"Verbindung zu {self.exchange_id} hergestellt. {len(markets)} Märkte geladen.")

    async def close(self) -> None:
        if self.exchange:
            await self.exchange.close()

    async def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> pd.DataFrame:
        """Holt Kerzen-Daten und gibt sie als DataFrame zurück."""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        except Exception as e:
            logger.error(f"Fehler beim Laden von OHLCV ({symbol}): {e}")
            return pd.DataFrame()

    async def get_active_markets(self, quote: str = "USDT") -> list[str]:
        """Filtert Märkte nach Quote-Währung."""
        if not self.exchange:
            return []
        markets = self.exchange.markets
        return [s for s, m in markets.items() if m["active"] and m["quote"] == quote]
