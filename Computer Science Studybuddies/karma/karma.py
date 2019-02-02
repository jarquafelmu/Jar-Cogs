from redbot.core import Config, commands, checks
from redbot.core.utils.chat_formatting import error
from redbot.core.utils.predicates import MessagePredicate

import discord
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


class Karma(commands.Cog):
    """
    Handles functions regarding karma
    """
    thumbs_up_emoji = "\N{Thumbs Up Sign}"
    properties = {
        "guild": None
    }
    attr_names = {
        "thanked": "been_thanked",
        "thanking": "thanked_others"
    }

    def __init__(self, bot):
        """Initialization function"""
        self.bot = bot
        self.db = Config.get_conf(self, identifier=1742113358,
                                  force_registration=True)

        default_member = {
            "been_thanked": {
                "total": 0,
                "current": 0
            },
            "thanked_others": {
                "total": 0,
                "current": 0
            }
        }

        self.db.register_member(**default_member)

    @commands.group(name="karma", aliases=["k", "Karma"])
    async def _karma(self, ctx):
        """
        A group of commands for the karma cog
        """
        pass

    @_karma.command(name="check", aliases=["c"])
    async def _karma_check(self, ctx, member: discord.Member):
        """
        Displays a user's karma score.
        """
        def build_field(group):
            return (
                f"**Current:** {group['current']}\n"
                f"**All Time:** {group['total']}"
            )

        try:
            been_thanked = build_field(
                await self.db.member(member).been_thanked()
            )
            thanked_others = build_field(
                await self.db.member(member).thanked_others()
            )
        except KeyError:
            log.exception("Exception occured.")
            await ctx.send(error("Member not found."))
        else:
            embed = discord.Embed(color=0xEE2222,
                                  title=f"{member.name}'s karma")
            embed.add_field(name="Thanked by others",
                            value=been_thanked,
                            inline=False)
            embed.add_field(name="Thanked others",
                            value=thanked_others,
                            inline=False)
            await ctx.send(embed=embed)

            log.info(
                "{\n"
                f"  member: {member.name}\n"
                f"  been_thanked: {been_thanked}\n"
                f"  thanked_others: {thanked_others}"
                "\n}"
            )
        pass

    @_karma.group(name="settings", aliases=["s", "set"])
    @checks.admin()
    async def _karma_settings(self, ctx):
        """
        A group of commands for managing the settings for the karma cog
        """
        pass

    @_karma_settings.command(name="reset")
    @checks.admin()
    async def _karma_settings_reset(self, ctx):
        """
        Clears the karma data.
        """
        # clears all the data stored for member of this guild in the database
        msg = (
            "Reset the karma for all members?"
            " There is **no** undo option!"
        )
        if await self.confirm(ctx, msg=msg):
            await self.db.clear_all_members(ctx.guild)
        await ctx.send("Done.")
        pass

    async def confirm(self, ctx, *, msg="Are you sure?"):
        """
        Handles confirmations for commands.

        Optionally can supply a message that is displayed to the user.
        Defaults to 'Are you sure?'.
        """
        await ctx.channel.send(f"{msg} (y/n)")
        pred = MessagePredicate.yes_or_no(ctx)
        await self.bot.wait_for("message", check=pred)
        return pred.result

    async def on_raw_reaction_add(self,
                                  payload: discord.RawReactionActionEvent):
        """
        Member agrees to the rules.
        """
        await self.process_reaction(payload=payload, is_add_action=True)
        pass

    async def on_raw_reaction_remove(self,
                                     payload: discord.RawReactionActionEvent):
        """
        Member no longer agrees to the rules.
        """
        await self.process_reaction(payload=payload, is_add_action=False)
        pass

    async def process_reaction(self, *,
                               payload: discord.RawReactionActionEvent,
                               is_add_action: bool):
        """
        Processes the reaction to see if it is a karma reaction.
        """
        if str(payload.emoji) != self.thumbs_up_emoji:
            return

        # get the guild from the payload
        if self.properties["guild"] is None:
            self.properties["guild"] = self.bot.get_guild(payload.guild_id)

        # get the member from the guild using the user_id in the payload
        member_giving = self.properties["guild"].get_member(payload.user_id)
        channel = self.properties["guild"].get_channel(payload.channel_id)
        message = await channel.get_message(payload.message_id)
        member_receiving = message.author

        if member_giving.id == member_receiving.id:
            return log.debug("member cannot give themselves karma.")

        if member_receiving.bot:
            return log.debug("bot may not receive karma.")

        modifier = 1 if is_add_action else -1

        log.debug(
            f"{member_giving.name} "
            f"{'gave a' if modifier == 1 else 'removed their'}"
            f" karma "
            f"{'to' if modifier == 1 else 'from'}"
            f" {member_receiving.name}"
        )

        await self.modify_karma(member_giving, member_receiving, modifier)
        pass

    async def modify_karma(self, member_giving, member_receiving, modifier):
        """
        Adds a karma point to both users
        """
        await self.update_karma_category(member_giving,
                                         self.attr_names["thanking"],
                                         modifier)

        await self.update_karma_category(member_receiving,
                                         self.attr_names["thanked"],
                                         modifier)
        pass

    def to_non_negative(self, val: int):
        """
        Returns either the `val` or zero.
        """
        return max(val, 0)

    async def update_karma_category(self,
                                    member: discord.Member,
                                    category_id: str,
                                    modifier: int):
        """
        Applies the modifier to the user's thanked score.
        """
        try:
            thank_category = await self.db.member(member).get_raw(category_id)

            thank_category["total"] = self.to_non_negative(
                thank_category["total"] + modifier
            )
            thank_category["current"] = self.to_non_negative(
                thank_category["current"] + modifier
            )

            await self.db.member(member).set_raw(category_id,
                                                 value=thank_category)
        except KeyError:
            log.exception("Exception occured.")
