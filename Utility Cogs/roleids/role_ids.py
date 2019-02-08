from redbot.core import commands
from redbot.core.utils.chat_formatting import pagify, bold

import logging


# create log with 'spam_application'
log = logging.getLogger("karma.py")
log.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter(
    "%(asctime)s - %(name)s::%(funcName)s::%(lineno)d"
    "- %(levelname)s - %(message)s"
)

# create console handler
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(formatter)

# add the handlers to the log
print('adding handler-')
# allows to add only one instance of file handler and stream handler
if log.handlers:
    print('making sure we do not add duplicate handlers')
    for handler in log.handlers:
        # add the handlers to the log
        # makes sure no duplicate handlers are added

        if not isinstance(handler, logging.StreamHandler):
            log.addHandler(consoleHandler)
            print('added stream handler')
else:
    log.addHandler(consoleHandler)
    print('added handler for the first time')


class RoleIds(commands.Cog):
    """Retreives a list of server roles and their ids"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def getIds(self, ctx):
        """displays a list of server roles and their ids"""

        roles = []
        async with ctx.channel.typing():
            for role in ctx.guild.roles:
                roles.append(f"{role.name}: {role.id}")
                log.debug(f"added {role.name}")

            out = "\n".join(roles)
            pages = pagify(out)

            await ctx.send(bold("Role Name: Role Id"))
            for page in pages:
                await ctx.send(page)
