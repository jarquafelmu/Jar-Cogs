"""Add this cog to the bot"""
from .prune_channels import PruneChannels


async def setup(bot):
    """Setup this cog"""
    cog = PruneChannels(bot)
    bot.add_cog(cog)
