from redbot.core import commands
from .logger import logger
import asyncio

class Utility(commands.Cog):  
    def __init__(self, bot):
        self._ready = asyncio.Event()
        self._init_task = None
        self._ready_raised = False

    def create_init_task(self):
        def _done_callback(task):
            exc = task.exception()
            if exc is not None:
                logger.error(
                    "An unexpected error occurred during OnStudy's initialization.", exc_info=exc
                )
                self._ready_raised = True
            self._ready.set()

        self._init_task = asyncio.create_task(self.initialize())
        self._init_task.add_done_callback(_done_callback)

    async def initialize(self):
        # alternatively use wait_until_red_ready() if you need some stuff that happens in our post-connection startup
        await self.bot.wait_until_ready()
        # do what you need

    def cog_unload(self):
        if self._init_task is not None:
            self._init_task.cancel()

    async def cog_before_invoke(self, ctx):
        # use if commands need initialize() to finish
        async with ctx.typing():
            await self._ready.wait()
        if self._ready_raised:
            await ctx.send(
                "There was an error during OnStudy's initialization. Check logs for more information."
            )
            raise commands.CheckFailure()
        
    async def wait(self):
      self._load_event.wait()
      if self._ready_raised:
        return False