from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import warning

import discord
import contextlib

# TODO: update for rules role and the others
# TODO: Create tool where a role can be assigned to a reaction emoji from bot commands

class RoleManager(commands.Cog):
    """Manages roles for Server McServerface"""

    guild_id = 493875452046475275

    msg_rule_agreement_id = 508393348067885066
    msg_author_id = 513857600152928279

    log_id = 509041710651670548

    def __init__(self, bot):
        self.bot = bot
        self.log = self.bot.get_channel(self.log_id)

        self.db = Config.get_conf(self, identifier=1742113358, force_registration=True)

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
        self.roles = {
            "member": {
                "id": 567886671245475869
            },
            "reader": {
                "id": 506657944860098561
            },
            "author": {
                "id": 506657837498368014
            }
        }

        self.roles["member"]["obj"] = self.bot.get_guild(
            self.guild_id).get_role(self.roles["member"]["id"])
        self.roles["reader"]["obj"] = self.bot.get_guild(
            self.guild_id).get_role(self.roles["reader"]["id"])
        self.roles["author"]["obj"] = self.bot.get_guild(
            self.guild_id).get_role(self.roles["author"]["id"])

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        """
        Member agrees to the rules
        """
        await self.process_reaction(payload, True)

    @commands.Cog.listener("on_raw_reaction_remove")
    async def on_raw_reaction_remove(self, payload):
        """
        Member no longer agrees to the rules
        """
        await self.process_reaction(payload, False)

    async def process_reaction(self, payload, add: bool):
        """
        Handles the processing of the reaction
        """
        member = self.bot.get_guild(self.guild_id).get_member(payload.user_id)

        if member is None:
            return

        print(payload.emoji)

        emoji = str(payload.emoji)

        print(emoji)

        msg_id = payload.message_id
        if msg_id == self.msg_rule_agreement_id:
            await self.process_rule_agreement_reaction(member, emoji, add)
        elif msg_id == self.msg_author_id:
            await self.process_author_reaction(member, emoji, add)

    async def process_rule_agreement_reaction(self, member: discord.Member, emoji: str, add: bool):
        """
        Handles the rule agreement reaction
        """

        if emoji.startswith("\N{THUMBS UP SIGN}"):
            if add:
                msg = (
                    f"Thank you for agreeing to the rules of {member.guild.name}.\n"
                    "You have now been granted full access to the server."
                )
                action = "added"
                await member.add_roles(self.roles["member"]["obj"])
            else:
                msg = (
                    f"It is unfortunate that you can no longer agree to the rules of {member.guild.name}.\n"
                    "Your access to the server has been restricted.\n"
                    "If you decide to agree to the rules in the future, your access will be restored."
                )
                action = "removed"
                await member.remove_roles(self.roles["member"]["obj"])

            await self.log.send(f"`{member.name}` {action} `member` role.")
            with contextlib.suppress(discord.HTTPException):
                # we don't want blocked DMs preventing the function working
                await member.send(msg)
        else:
            await self.log.send(warning(f"`{member.name}` tried to add a role but used the wrong emoji."))

    async def process_author_reaction(self, member: discord.Member, emoji: str, add: bool):
        """
        Handles the rule agreement reaction
        """

        if emoji.startswith("\N{LOWER LEFT BALLPOINT PEN}"):
            if add:
                action = "added"
                await member.add_roles(self.roles["author"]["obj"])
            else:
                action = "removed"
                await member.remove_roles(self.roles["author"]["obj"])
            await self.log.send(f"`{member.name}` {action} `author` role.")
        else:
            await self.log.send(warning(f"`{member.name}` tried to add a role but used the wrong emoji."))
