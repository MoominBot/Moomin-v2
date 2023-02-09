import logging
import math
import re
import traceback

import hikari
import lightbulb

logger = logging.getLogger("error_handler")
errors_plugin = lightbulb.Plugin("Errors")


@errors_plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    error = event.exception
    exc_info = event.exc_info
    error_id = await errors_plugin.bot.db.fetch_val(
        "INSERT INTO errors (message) VALUES ($1) RETURNING error_id",
        "".join(traceback.format_exception(*exc_info)),
    )
    if isinstance(error, lightbulb.CommandNotFound):
        return

    if isinstance(error, lightbulb.BotMissingRequiredPermission):
        missing = [
            perm.replace("_", " ").replace("guild", "server").title()
            for perm in str(error.missing_perms).split("|")
        ]
        if len(missing) > 2:
            fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = " and ".join(missing)

        _message = f"I need the **{fmt}** permission(s) to run this command."

        embed = hikari.Embed(
            title="I am Missing Permissions",
            color=0xFF0000,
            description=_message + f"```\nError ID: {error_id}```",
        )
        return await event.context.respond(
            embed=embed, flags=hikari.MessageFlag.EPHEMERAL
        )

    if isinstance(error, lightbulb.CommandIsOnCooldown):
        embed = hikari.Embed(
            title="Command on Cooldown",
            color=0xFF0000,
            description=f"This command is on cooldown, please retry in {math.ceil(error.retry_after)}s."
            + f"```\nError ID: {error_id}```",
        )
        return await event.context.respond(
            embed=embed, flags=hikari.MessageFlag.EPHEMERAL
        )

    if isinstance(error, lightbulb.NotEnoughArguments):
        return await event.bot.help_command.send_command_help(
            event.context, event.context.command
        )

    if isinstance(error, lightbulb.MissingRequiredPermission):
        missing = [
            perm.replace("_", " ").replace("guild", "server").title()
            for perm in str(error.missing_perms).split("|")
        ]
        if len(missing) > 2:
            fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = " and ".join(missing)
        _message = "You need the **{}** permission(s) to use this command.".format(fmt)

        embed = hikari.Embed(
            title="You are missing permissions",
            color=0xFF0000,
            description=_message + f"```\nError ID: {error_id}```",
        )
        return await event.context.respond(
            embed=embed, flags=hikari.MessageFlag.EPHEMERAL
        )

    title = " ".join(re.compile(r"[A-Z][a-z]*").findall(error.__class__.__name__))
    await event.context.respond(
        embed=hikari.Embed(
            title=title,
            description=str(error) + f"```\nError ID: {error_id}```",
            color=0xFF0000,
        ),
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    raise error


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(errors_plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(errors_plugin)
