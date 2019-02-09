from .karma import Karma
from .css import CSS
from .courses import Courses
from .logger import Logger

guild_id = 481613220550017036


async def setup(bot):
    # logger stuff
    cog = Logger(bot, guild_id)
    bot.add_cog(cog)

    # Karma cog stuff
    cog = Karma(bot)
    bot.add_cog(cog)

    # Courses cog stuff
    cog = Courses(bot)
    bot.add_cog(cog)

    # CSS cog stuff
    cog = CSS(bot)
    bot.add_cog(cog)
    await cog.is_loaded()
