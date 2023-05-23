# pylint: disable=too-few-public-methods
"""Prunes a selection of channels from a server."""
from redbot.core import commands
from redbot.core.utils.chat_formatting import error, info
from redbot.core.utils.predicates import MessagePredicate

import discord


class PruneChannels(commands.cog):
    """Prunes a selection of channels from a server."""

    def __init__(self, bot):
        """Initializes this bot"""
        self.bot = bot
        self.guild_id = 481613220550017036

    @commands.command()
    async def prune(self, ctx):
        """Prunes the channels of the server
        """
        channels = self.bot.get_guild(self.guild_id).voice_channels
        channels = channels[:5]
        length = len(channels)
        await ctx.send(f'Found {length} channels that match characteristics.')
        confirm = await self.confirm(
            ctx,
            msg="Are you sure you wish to delete these channels? THERE IS NO UNDO."
        )

        if not confirm:
            return await ctx.send("Canceling.")

        await ctx.send(
            'Attempting to delete channels. This might take a while.'
            + 'Please wait for me to stop typing.'
        )
        self.remove_channels(ctx, channels)
        await ctx.send('Finished deleting channels.')

    async def confirm(self, ctx, *, msg="Are you sure?"):
        """
        Handles confirmations for commands.
        Optionally can supply a message that is displayed to the user. Defaults to 'Are you sure?'.
        """
        await ctx.channel.send(f"{msg} (y/n)")
        pred = MessagePredicate.yes_or_no(ctx)
        await self.bot.wait_for("message", check=pred)
        return pred.result


async def remove_channels(ctx, channels):
    """Deletes all channels of this type from the server"""
    async with ctx.typing():
        for channel in channels:
            name = channel.name
            try:
                await channel.delete(f'Pruning voice channel {name} to alleviate bloat.')
            except discord.NotFound:
                await ctx.send(info(f"The channel {name} has already been deleted."))
            except discord.Forbidden:
                await ctx.send(error(f"Forbidden from deleting channel {name}."))
            except discord.HTTPException:
                await ctx.send(error(f"Retrieving channel {name} failed."))
