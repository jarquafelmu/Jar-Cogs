from redbot.core import commands
from redbot.core.utils.chat_formatting import pagify, bold
import emoji

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


class Emoji(commands.Cog):
    """Retreives a list of server roles and their ids"""

    def __init__(self, bot):
        self.bot = bot
        pass

    @commands.command(name="emojitotext")
    async def emojiToText(self, ctx, emojiInput):
        """
        A spike to see if converting an emoji glyph into it's name works
        """
        if (not emoji):
            await ctx.channel.send("You must supply an emoji!")

        decodedEmoji = repr(emoji.demojize(emojiInput, use_aliases=True))
        await ctx.channel.send(f"With Alias: Emoji: {emojiInput}, Decoded name: {decodedEmoji}")
        decodedEmoji = repr(emoji.demojize(emojiInput))
        await ctx.channel.send(f"Without Alias: Emoji: {emojiInput}, Decoded name: {decodedEmoji}")
        pass

    @commands.command(name="testequality")
    async def testEquality(self, ctx, emoji1, emoji2):
        if (not emoji1 or not emoji2):
            await ctx.channel.send("You must supply emojis!")

        # check if glyphs are equal
        await ctx.channel.send(f"Are {emoji1} and {emoji2} equal? {emoji1 == emoji2}")

        # check if decoded names are equal
        emoji1 = emoji.demojize(emoji1)
        emoji2 = emoji.demojize(emoji2)
        await ctx.channel.send(f"Are {emoji1} and {emoji2} equal? {emoji1 == emoji2}")

        emoji1 = emoji1.replace(r':', '')
        emoji2 = emoji2.replace(r':', '')
        # check if both emoji start the same
        await ctx.channel.send(f"Does {emoji2} start with {emoji1}? {emoji2.startswith(emoji1)}")
        pass
