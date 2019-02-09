from redbot.core import checks, commands
from redbot.core.utils.chat_formatting import humanize_list
from redbot.core.utils.predicates import MessagePredicate
import discord


class CSS(commands.Cog):
    """
    Custom functions to handle running the Computer Science Studybuddies server
    """

    guild_id = 481613220550017036
    utility_roles = {
        "admin": {
            "id": 484368083897679882,
            "ref": None
        },
        "staff": {
            "id": 492382906241777678,
            "ref": None
        }
    }

    def __init__(self, bot):
        """Initialization function"""
        self.bot = bot
        self.guild = self.bot.get_guild(self.guild_id)
        self.channels = self.Channels(bot)

        self.utility_roles["admin"]["ref"] = self.guild.get_role(self.utility_roles["admin"]["id"])
        self.utility_roles["staff"]["ref"] = self.guild.get_role(self.utility_roles["staff"]["id"])

    class Channels:
        """
        Enum for channels to make it simplier to access them when needed
        """

        def __init__(self, bot):
            self.bot = bot

        course_list_id = 514518408122073116
        log_id = 485218362272645120
        new_members_id = 484378858968055814
        roles_id = 482361038478508034
        welcome_id = 514572072794587136

        @property
        def courseList(self):
            """Logging channel object"""
            return self.bot.get_channel(self.course_list_id)

        @property
        def log(self):
            """Logging channel object"""
            return self.bot.get_channel(self.log_id)

        @property
        def newMembers(self):
            """New Members channel object"""
            return self.bot.get_channel(self.new_members_id)

        @property
        def roles(self):
            """Roles channel object"""
            return self.bot.get_channel(self.roles_id)

        @property
        def welcome(self):
            """Server Guidelines channel object"""
            return self.bot.get_channel(self.welcome_id)

        def anchor(self, channel):
            """Formats the channel for embedding in a string"""

            return f"<#{channel}>"

    def getRoleList(self, user: discord.Member = None):
        """
        Gets a list of the roles assigned to the user,
        omitting the '@everyone' role
        """

        if user is None:
            return []

        return [role.name for role in user.roles if role.name != "@everyone"]

    async def confirm(self, ctx, *, msg="Are you sure?"):
        """
        Handles confirmations for commands.

        Optionally can supply a message that is displayed to the user. Defaults to 'Are you sure?'.
        """

        await ctx.channel.send(f"{msg}")
        pred = MessagePredicate.yes_or_no(ctx)
        await self.bot.wait_for("message", check=pred)
        return pred.result

    async def pastGreet(self, ctx=None):
        """
        Greets members that joined the server while the bot was unavailable
        """

        recentlyJoinedMembers = []
        messageLimit = 50

        log = self.channels.log

        if log is None:
            return

        # scan through the `messageLimit` most recent messages, add any new member announcment to the list of
        # `recentlyJoinedMembers` exit as soon as there is message from the bot found
        async for message in self.channels.newMembers.history(limit=messageLimit):
            if not message.author.bot:
                if message.type == discord.MessageType.new_member:
                    recentlyJoinedMembers.append(message)
            else:
                break

        size = len(recentlyJoinedMembers)
        await log.send(f"{size} new member{'s' if size > 1 or size == 0 else ''} greeted since I was last online.")

        # if our list is empty then we don't want to do anything else
        if size == 0:
            return

        members = [message.author for message in recentlyJoinedMembers]

        #  for message in recentlyJoinedMembers:
        await self.welcome(self.channels.newMembers, members)
        pass

    async def prodMember(self, ctx, user: discord.Member = None):
        """
        DM's the user asking them to tell the server what courses they have
        """

        if user is None:
            return

        log = self.channels.log

        await user.send(
            f"Hi {user.display_name}.\n"
            "You have been on the **{user.guild.name}** discord server for a bit but haven't signed up for any courses.\n\n"
            "In order to get the most use out of the server you will need to do that so that you can see the groups for your courses.\n\n"
            "Don't reply to this message as this is just a bot.\n"
            f"Instead visit server and grab your courses in the **#{self.channels.courseList.name}** channel. Hope to see you soon."
        )

        await log.send(f"Prodded **{user.display_name}** as requested.")
        pass

    async def welcome(self, channel=None, members=None):
        """
        Helper function to handle the welcoming of a user
        """

        # We don't want to do anything if we don't have a channel or any members
        if channel is None or members is None:
            return

        # if members isn't already a list, then make it one
        if not isinstance(members, list):
            members = [members]

        size = len(members)

        # if the list is empty then return as we are done
        if size == 0:
            return

        mentionList = [member.mention for member in members]

        await channel.send(
            f"Welcome {humanize_list(mentionList)}! Check out the {self.channels.anchor(self.channels.welcome_id)} channel for some information about the server."
        )
        pass

    # user commands
    @commands.command()
    @checks.mod()
    async def greet(self, ctx, user: discord.Member = None):
        """
        Welcomes a user to the server
        """
        if user is None:
            user = ctx.author

        await self.welcome(ctx, user)

        await ctx.channel.send("Done.")
        pass

    @commands.command()
    @checks.admin()
    async def prod(self, ctx, user: discord.Member = None):
        """
        DM's the user asking them to tell the server what courses they have
        """

        if user is None:
            return

        # single user
        await self.prodMember(ctx, user)

        await ctx.channel.send("Done.")
        pass

    @commands.command()
    @checks.admin()
    async def prodAll(self, ctx):
        """
        Prods all members of the server, using DM's, who do not currently have any roles

        Can only be used by admins.
        """
        confirmed = await self.confirm(ctx)

        if confirmed:
            # build list of members without roles
            membersWithoutRoles = [member for member in ctx.guild.members if len(member.roles) < 2]

            log = self.channels.log

            size = len(membersWithoutRoles)
            if size == 0:
                return await ctx.send("All members are have courses.")

            await ctx.send(f"Prodding {size} member{'s' if size > 1 or size == 0 else ''}.")

            async with log.typing():
                for member in membersWithoutRoles:
                    await self.prodMember(ctx, member)

            # announce that the bot is done prodding members
            await log.send(f"\n\nCompleted prodding necessary members.")

            await ctx.send(f"Finished.")
        else:
            return await ctx.send("Standing down.")
        pass

    # custom events
    async def is_loaded(self):
        """
        Handles actions that are done when the bot is loaded and ready to work.
        """

        # await self.channels.log.send(f"Bot is loaded and ready.")
        await self.pastGreet()

    # event triggers
    async def on_member_join(self, member):
        """
        Welcome's a new user to the server
        """

        # we only want to announce if this is the right server
        if member.guild.id != self.guild.id:
            return

        await self.welcome(self.channels.newMembers, member)
        pass

    async def on_member_remove(self, member):
        """
        event happens when a member leaves the server
        """
        # we only want to announce if this is the right server
        if member.guild.id != self.guild.id:
            return

        await self.channels.log.send(f"<@&{self.utility_roles['admin']['id']}>: {member.display_name} has left the building.")
        pass
