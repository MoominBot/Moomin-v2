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
            banner="moomin.assets",
            help_slash_command=True,
            default_enabled_guilds=[842033877563605012],
        )
        self.db = DatabaseManager(Config.PSQL_DSN)
        self.redis_cache = aioredis.Redis(host="redis")
        self.bidas = BidaCache(self)

    def start_moomin(self):
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.load_extensions_from("./moomin/plugins", recursive=True)

        super().run()

    async def on_starting(self, _: hikari.StartingEvent) -> None:
        self.session = aiohttp.ClientSession()
        logger.info("AioHTTP session initialized!")

        await self.db.establish_connection()

    async def on_started(self, _: hikari.StartedEvent) -> None:
        await self.db.migrate()
        await self.bidas.fetch()
        await self.bidas.get()

    async def on_stopping(self, _: hikari.StoppingEvent) -> None:
        await self.db.close_connection()
        await self.session.close()
        logger.info("aiohttp session closed.")
