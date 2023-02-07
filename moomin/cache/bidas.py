import logging
import pickle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from moomin.core.bot import Moomin

logger = logging.getLogger(__name__)


class BidaCache:
    def __init__(self, bot: "Moomin") -> None:
        self.bot = bot
        self.base_url = "https://api.nepalipatro.com.np/goverment-holidays/2079"

    async def fetch(self):
        async with self.bot.session.get(self.base_url) as resp:
            if resp.status == 200:
                data = await resp.json()

        await self.bot.redis_cache.set("bidas", pickle.dumps(data))
        logger.info("[Redis - Bidas] Bidas cached successfully!")

        return data

    async def get(self):
        cache = await self.bot.redis_cache.get("bidas")
        if not cache:
            return None
        return pickle.loads(cache)
