from asyncio.windows_events import NULL
from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import warning

import emoji
import discord
import contextlib

# TODO: update for rules role and the others
# TODO: Create tool where a role can be assigned to a reaction emoji from bot commands


class RoleManager(commands.Cog):
    """Manages roles for Server McServerface"""

    guild_id = 493875452046475275
    log_id = 509041710651670548
    log_channel = None
    role_to_test = "member"
    roles = {
        "member": {"id": 567886671245475869, "msg_id": 508393348067885066, "emoji": '👍'},
        "reader": {"id": 506657944860098561, "msg_id": 569318277612961822, "emoji": '📖'},
        "author": {"id": 506657837498368014, "msg_id": 569318277612961822, "emoji": '✏️'},
        "beta_reader": {"id": 565022046279696396, "msg_id": 569318277612961822, "emoji": '👓'},
        "editor": {"id": 564972131541188609, "msg_id": 569318277612961822, "emoji": '🖊️'},
        "site_staff": {"id": 569281650802819074, "msg_id": 569318277612961822, "emoji": '💻'},
        "artist": {"id": 578703388263317565, "msg_id": 569318277612961822, "emoji": '🖌️'}
    }

    def __init__(self, bot):
        self.bot = bot
        pass

    async def get_guild(self):
        """Gets a discord guild reference

        Args:
            id (number): The guild id
        """
        return await self.bot.fetch_guild(self.guild_id)

    async def get_channel(self, id):
        """Gets a channel of the guild

        Args:
            id (number): The channel id
        """
        guild = await self.get_guild()
        return guild.get_channel(id)

    async def get_role(self, id):
        """[summary]

        Args:
            id ([type]): [description]

        Returns:
            [type]: [description]
        """
        guild = await self.get_guild()
        return guild.get_role(id)

    async def log(self, msg):
        """Logs a message to the guild channel set up for logging

        Args:
            msg (str): the message to be sent
        """
        if not self.log_channel:
            self.log_channel = self.bot.get_channel(self.log_id)
        await self.log_channel.send(msg)
        pass

    @commands.command(name="test_role")
    async def changeRoleToBeTested(self, ctx, role):
        previous_role = self.role_to_test
        self.role_to_test = role
        await ctx.channel.send(f"Changed testing role from {previous_role} to {self.role_to_test}")
        await ctx.channel.send(f"Using emoji: {self.roles[self.role_to_test]['emoji']}")
        pass

    @commands.Cog.listener("on_raw_reaction_add")
    async def reaction_added(self, payload):
        """
        Member added a reaction to a messsage
        """
        await self.process_reaction(payload, True)
        pass

    @commands.Cog.listener("on_raw_reaction_remove")
    async def reaction_removed(self, payload):
        """
        Member removed a reaction from a messsage
        """
        await self.process_reaction(payload, False)
        pass

    async def process_reaction(self, reaction, add: bool):
        """
        Handles the processing of the reaction
        """
        member = self.bot.get_guild(self.guild_id).get_member(reaction.user_id)

        if member is None:
            return print("Member wasn't found in guild")
        # does this reaction come from a message that we are monitoring?

        role = None
        role_name = None

        # iterate over roles
        for (key, value) in self.roles.items():
            # value is a role property, key is the name of the role
            if (value["msg_id"] == reaction.message_id and value["emoji"] == str(reaction.emoji)):
                role_name = key
                role = value

        if role is None:
            return print("No role matched for this message and emoji")

        role_obj = await self.get_role(role["id"])
        if add:
            action = "added"
            await member.add_roles(role_obj)
        else:
            action = "removed"
            await member.remove_roles(role_obj)

        await self.log(f"`{member.name}` {action} `{role_name} ({role['emoji']})` role.")
        print(f"`{member.name}` {action} `{role_name}` role.")
        pass
