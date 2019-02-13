from redbot.core import commands
from redbot.core.utils.predicates import MessagePredicate


class Logic(commands.Bot):

    def __init__(self, bot):
        """
        Initialize the CourseAssignment object
        """
        self.bot = bot    

    async def confirm(self, ctx, *, msg="Are you sure?"):
        """
        Handles confirmations for commands.
        Optionally can supply a message that is displayed to the user. Defaults to 'Are you sure?'.
        """
        await ctx.channel.send(f"{msg} (y/n)")
        pred = MessagePredicate.yes_or_no(ctx)
        await self.bot.wait_for("message", check=pred)
        return pred.result