from .mycog import Mouse


async def setup(bot):
    cog = Mouse(bot)
    bot.add_cog(cog)
    await cog.is_loaded()
