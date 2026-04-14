import asyncio
import logging
import signal
import sys
from typing import TYPE_CHECKING

# Relative imports modified for flat src/ structure if needed,
# but keeping original structure as requested by path.
from exchange.wrapper import ExchangeWrapper
from strategy.signal_aggregator import SignalAggregator
from utils import load_config, setup_logging

if TYPE_CHECKING:
    from strategy.decision import Decision

logger = logging.getLogger(__name__)


class TradingBot:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.running = False
        self.exchange = ExchangeWrapper(config)
        self.aggregator = SignalAggregator(config)
        self.scalping_mode = config.get("bot", {}).get("scalping_mode", False)

    async def start(self) -> None:
        """Hauptschleife des Bots."""
        self.running = True
        logger.info(f"Bot gestartet (Mode: {self.config.get('bot', {}).get('mode')})")

        # Initialisierung
        await self.exchange.initialize()

        while self.running:
            try:
                if self.scalping_mode:
                    await self._run_scalping_loop()
                else:
                    await self._run_standard_loop()

                # Pause zw. Zyklen
                interval = self.config.get("scanner", {}).get("scan_interval", 60)
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Fehler in Hauptschleife: {e}", exc_info=True)
                await asyncio.sleep(10)

    async def stop(self) -> None:
        """Bot sauber beenden."""
        self.running = False
        logger.info("Bot wird beendet...")
        await self.exchange.close()

    async def _run_standard_loop(self) -> None:
        """Standard Swing/Daytrading Analyse."""
        logger.debug("Starte Analyse-Zyklus...")
        # 1. Märkte scannen
        markets = await self.exchange.get_active_markets()

        for symbol in markets:
            # 2. Daten laden
            df = await self.exchange.fetch_ohlcv(symbol)
            if df.empty:
                continue

            # 3. Signale berechnen
            decision: "Decision" = self.aggregator.analyze(df, symbol, self.exchange.name, "1h")

            # 4. Entscheidung ausführen (Logik folgt...)
            if decision.is_actionable:
                logger.info(f"SIGNAL für {symbol}: {decision.signal}")

    async def _run_scalping_loop(self) -> None:
        """Schnelles Scalping (Watchlist-basiert)."""
        watchlist = self.config.get("scalping", {}).get("watchlist", [])
        # ... logic ...
        pass


async def main():
    # 1. Config & Logging
    try:
        config = load_config()
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {e}")
        sys.exit(1)

    setup_logging(level=config.get("bot", {}).get("log_level", "INFO"))

    # 2. Bot Instanz
    bot = TradingBot(config)

    # 3. Task Management
    bot_task = asyncio.create_task(bot.start())

    try:
        await bot_task
    except asyncio.CancelledError:
        pass
    finally:
        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
