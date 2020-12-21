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

    def get_guild(self):
        """Gets a discord guild reference

        Args:
            id (number): The guild id
        """
        return self.bot.get_guild(self.guild_id)

    def get_channel(self, id):
        """Gets a channel of the guild

        Args:
            id (number): The channel id
        """
        return self.get_guild().get_channel(id)

    def get_role(self, id):
        """Gets a role from the server

        Args:
            id (number): The role id
        """
        return self.get_guild().get_role(id)

    def get_member(self, id):
        """Gets a member from the server

        Args:
            id (number): The member id
        """
        return self.get_guild().get_member(id)

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

    def determine_role(self, reaction):
        for (key, value) in self.roles.items():
            # value is a role property, key is the name of the role
            if (value["msg_id"] == reaction.message_id and value["emoji"] == str(reaction.emoji)):
                return (key, value)
        return (None, None)

    @commands.Cog.listener("on_raw_reaction_add")
    @commands.Cog.listener("on_raw_reaction_remove")
    async def process_reaction(self, reaction):
        """
        Handles the processing of the reaction

        Args:
            reaction (RawReactionActionEvent): The reaction sent from the server
            add (bool): If True, adds a role to the user. Otherwise, removes a role from the user
        """
        member = self.get_member(reaction.user_id)

        if member is None:
            return print("Member wasn't found in guild")
        # does this reaction come from a message that we are monitoring?

        (role_name, role) = self.determine_role(reaction)

        if role is None:
            return print("No role matched for this message and emoji")

        role_obj = self.get_role(role["id"])
        if reaction.event_type == "REACTION_ADD":
            action = "added"
            await member.add_roles(role_obj)
        else:
            action = "removed"
            await member.remove_roles(role_obj)

        await self.log(f"`{member.name}` {action} `{role_name} ({role['emoji']})` role.")
        print(f"`{member.name}` {action} `{role_name}` role.")
        pass
