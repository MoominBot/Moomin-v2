import logging
import pickle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from moomin.core.bot import Moomin

logger = logging.getLogger(__name__)


class Bida(object):
    def __init__(
        self,
        bs: str,
        ad: str,
        title: str,
        bs_month: int,
        *args,
        **kwargs,
    ):
        self.bs = bs
        self.ad = ad
        self.title = title
        self.bs_month = bs_month


class BidaCache:
    def __init__(self, bot: "Moomin") -> None:
        self.bot = bot
        self.base_url = "https://api.nepalipatro.com.np/goverment-holidays/2079"

    async def fetch(self):
        async with self.bot.session.get(self.base_url) as resp:
            if resp.status == 200:
                data = await resp.json()

                # Setting the bidas in the cache by converting
                # the json data into bytes
                await self.bot.redis_cache.set("bidas", pickle.dumps(data))
                logger.info("[Redis - Bidas] Bidas cached successfully!")

                return Bida(**data)
            else:
                raise Exception("Couldn't fetch data from the API")

    async def get(self):
        cache = await self.bot.redis_cache.get("bidas")
        if not cache:
            return None
        # Unpickling the data from bytes to json
        # and converting it to python objects
        return [Bida(**data) for data in pickle.loads(cache)]
