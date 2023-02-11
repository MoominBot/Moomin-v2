from typing import TYPE_CHECKING, cast

import hikari
import lightbulb
import miru
from miru.ext import nav

from moomin.utils.utils import _chunk

if TYPE_CHECKING:
    from moomin.core.bot import Moomin

owner = lightbulb.Plugin("Owner", "Commands that are meant for the bot owner")
owner.add_checks(lightbulb.owner_only)


@owner.command
@lightbulb.command("errors", "List all the errors from the database")
@lightbulb.implements(lightbulb.SlashCommand)
async def get_errors(ctx: lightbulb.Context) -> None:
    bot = cast("Moomin", owner.bot)
    data = await bot.db.fetch_all("SELECT * FROM errors")
    if data is None:
        return ctx.respond(
            embed=hikari.Embed(description="No errors could be found!", color=0xFF0000),
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    errors = [
        f"Error ID```\n{model.get('error_id')}```\n Error:```py\n{model.get('message')}```"
        for model in data
    ]

    fields = [
        hikari.Embed(color=0xFF0000, title="Error List", description="\n\n".join(error))
        for _, error in enumerate(_chunk(errors, 1))
    ]
    navigator = nav.NavigatorView(pages=fields)
    await navigator.send(ctx.interaction, ephemeral=True)
    await navigator.wait()


@owner.command
@lightbulb.option("error_id", "ID of the error")
@lightbulb.command("error", "Get details about a specific error", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_error(ctx: lightbulb.Context, error_id: str) -> None:
    bot = cast("Moomin", owner.bot)
    try:
        record = await bot.db.fetch_record(
            "SELECT * FROM errors WHERE error_id=$1", error_id
        )
    except Exception:
        return await ctx.respond(
            embed=hikari.Embed(
                description="No Error with that specified ID found",
                color=0xFF0000,
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    embed = hikari.Embed(
        title="Error Details",
        description=f"Error ID```\n{record.get('error_id')}```\n Error:```py\n{record.get('message')}```",
        color=0xFF0000,
    )
    await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(owner)
    miru.install(bot)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(owner)
