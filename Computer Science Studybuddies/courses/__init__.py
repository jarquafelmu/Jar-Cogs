from .courses import Courses


async def setup(bot):
    cog = Courses(bot)
    bot.add_cog(cog)
