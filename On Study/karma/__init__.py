from .karma import Karma

async def setup(bot):
    cog = Karma(bot)
    bot.add_cog(cog)
