import logging

import aiohttp
import aioredis
import hikari
import lightbulb

from moomin.cache.bidas import BidaCache
from moomin.utils.config import Config
from moomin.utils.database import DatabaseManager

logger = logging.getLogger(__name__)


class Moomin(lightbulb.BotApp):
    def __init__(self) -> None:
        super().__init__(
            token=Config.TOKEN,
            ignore_bots=True,
            intents=hikari.Intents.ALL,
            owner_ids=Config.OWNER_IDS,
        )
        self.db = DatabaseManager(Config.PSQL_DSN)
        self.redis_cache = aioredis.Redis()
        self.bidas = BidaCache(self)

    def start_moomin(self):
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.load_extensions_from("./moomin/plugins")

        super().run()

    async def on_starting(self, _: hikari.StartingEvent) -> None:
        self.session = aiohttp.ClientSession()
        logger.info("AioHTTP session initialized!")

        await self.db.establish_connection()

    async def on_started(self, _: hikari.StartedEvent) -> None:
        await self.db.migrate()
        await self.bidas.fetch()

    async def on_stopping(self, _: hikari.StoppingEvent) -> None:
        await self.db.close_connection()
        await self.session.close()
        logger.info("aiohttp session closed.")
