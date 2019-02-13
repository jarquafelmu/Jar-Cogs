from redbot.core import commands
import discord


class RoleHandler(commands.Cog):
    def __init__(self, bot):
        """
        Initialize the CourseAssignment object
        """
        self.bot = bot
        # self.guild = self.bot.get_guild(self.guild_id)
        # self.db = Config.get_conf(self, identifier=8748107325)
        # self.course_list = self.bot.get_channel(514518408122073116)
        # self.emoji = "\N{WHITE HEAVY CHECK MARK}"
        # self.utility_roles["staff"]["ref"] = self.guild.get_role(
        #     self.utility_roles["staff"]["id"]
        # )

        # default_guild = {
        #     "registered_courses": {}
        # }

        # self.db.register_guild(**default_guild)
        pass

    def getRoleList(self, user: discord.Member = None):
        """
        Gets a list of the roles assigned to the user,
        omitting the '@everyone' role
        """

        if user is None:
            return []

        return [role.name for role in user.roles if role.name != "@everyone"]