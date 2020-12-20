from .emoji import Emoji


async def setup(bot):
    cog = Emoji(bot)
    bot.add_cog(cog)
