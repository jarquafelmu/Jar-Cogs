from .css import CSS


async def setup(bot):
    cog = CSS(bot)
    bot.add_cog(cog)
    await cog.is_loaded()
