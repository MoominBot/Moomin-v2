import time
from datetime import datetime
from typing import TYPE_CHECKING, cast

import hikari
import lightbulb

from . import month_map

if TYPE_CHECKING:
    from moomin.core.bot import Moomin

general = lightbulb.Plugin("General")


@general.command
@lightbulb.option(
    "month",
    "Month whose bida you want",
    choices=[c for c in month_map.keys()],
    required=True,
)
@lightbulb.command("bida", "Show all the bidas of the current month", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def bida_command(ctx: lightbulb.Context, month: str):
    bot = cast("Moomin", general.bot)
    # Trying to get data from Redis Cache
    data = await bot.bidas.get()
    if not data:
        # If data doesn't exist fetch the data directly from the API
        # This also saves the data in the cache for future use
        data = await bot.bidas.fetch()

    embed = hikari.Embed(title=f"Bidas for {month}", color=0x00FF00).set_thumbnail(
        "https://i.ytimg.com/vi/jLJR26ha65g/hqdefault.jpg"
    )
    description = ""
    for info in data:
        if info.bs_month == month_map[month]:
            date = "-".join(info.bs.split(".")[::-1])
            timestamp = int(
                time.mktime(datetime.strptime(info.ad, "%Y-%m-%d").timetuple())
            )
            description += f"**{info.title}** - {date} • <t:{timestamp}:R>\n"

    embed.description = description

    embed.set_footer(
        text="Powered by Nepali Patro",
        icon="https://play-lh.googleusercontent.com/GAlzjx0HV_9KVafPrtcOR94fYbM4SVz8WaXCEsccoUzyYOu8K9IH1UYHvfMHNPTgSSQ",
    )

    await ctx.respond(embed=embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(general)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(general)
