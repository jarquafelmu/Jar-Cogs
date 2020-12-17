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

        self.db = Config.get_conf(
            self, identifier=1712118358, force_registration=True)

        default_guild = {
            "reaction_roles": []
        }
        }

        self.db.register_guild(**default_guild)
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

    @commands.command(name="registerReactionRole")
    async def registerRole(self, ctx):

        pass

    async def getRoleFromServer(self, role_id: str) -> str:
        """
        Gets a role from the server that matches the passed in id

        Args:
            role_id (str): The role to nab

        Returns:
            json: A reference to the role
        """
        return self.bot.get_guild(self.guild_id).get_role(role_id)

    async def getReactionRoles(self, ctx):
        """Gets the reaction roles from the database

        Args:
            ctx (obj): current context

        Returns:
            json: The reaction roles stored in the database
        """
        return await self.db.guild(ctx.guild).reaction_roles()

    async def storeReactionRoles(self, ctx, roles):
        """
        Stores the reaction roles in the database

        Args:
            ctx (obj): current context
            roles (json): A collection of reaction roles
        """
        await self.db.guild(ctx.guild).reaction_roles.set(roles)
        pass

        def createNewReactionRole(self, name: str, msg_id: str, role_id: str, emoji: str, emoji_name: str = ''):
            """Creates a new reaction role object

            Args:
                name (str): The name of the this reaction role
                msg_id (str): The id of the message that should be watched for reactions
                role_id (str): The role to be given or removed
                emoji (str): The triggering emoji
                "emoji_name": The string name of the emoji [Optional]

            Returns:
                json: {
                "name": str,
                "msg_id": str,
                "role_id": str,
                "emoji": str,
                "emoji_name": str
            }
            """
            return {
                "name": name,
                "msg_id": msg_id,
                "role_id": role_id,
                "emoji": emoji,
                "emoji_name": emoji_name
            }
