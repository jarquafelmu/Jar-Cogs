from .courses import Courses
from .css import CSS
from .karma import Karma
from .logic import Logic
from .oschannels import OSChannels
from .rolehandler import RoleHandler


async def setup(bot):
    args = {
        "guild_id": 481613220550017036,
        "channels": OSChannels(bot),
        "logic": Logic(bot)
    }

    args["roles"] = RoleHandler(bot, args)

    # Karma cog stuff
    cog = Karma(bot, args)
    bot.add_cog(cog)

    # Courses cog stuff
    cog = Courses(bot, args)
    bot.add_cog(cog)

    # CSS cog stuff
    cog = CSS(bot, args)
    bot.add_cog(cog)
    
    await cog.is_loaded()
