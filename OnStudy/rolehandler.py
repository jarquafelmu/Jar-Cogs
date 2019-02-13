from redbot.core import commands
from .logger import Logger, LogLevel
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

    def getRolesForUser(self, user: discord.Member = None):
        """
        Gets a list of the roles assigned to the user,
        omitting the '@everyone' role
        """

        if user is None:
            return []

        return [role.name for role in user.roles if role.name != "@everyone"]

    async def create_role(self, ctx, role_name: str):
        """
        Confirms that the user wants to create the role.
        If so the role is created and returned to the calling function.
        Otherwise, NoneType is returned.
        """
        createRole = await self.confirm(ctx, msg=f"Role `{role_name}` does not exist. Would you like to create it?")
        if (createRole):
            color = self.get_role_color()
            try:
                # create the role in the guild
                role_obj = await ctx.guild.create_role(name=role_name, color=color)
            except discord.InvalidArgument as e:
                self.logger.log("InvalidArgument", level=LogLevel.ERROR, exc_info=e)
            except discord.Forbidden as e:
                self.logger.log(f"Bot lacks permission to add roles to the server.", level=LogLevel.ERROR, exc_info=e)
            except discord.HTTPException as e:
                self.logger.log(f"Creating the role failed.", level=LogLevel.ERROR, exc_info=e)
            else:
                await self.logger.log(f"Creating role for {role_name}.", level=LogLevel.INFO)
                return role_obj
        return None

    def get_role_color(self):
        """
        Generates a random color for a role between 0xaaaaaa and 0xfffffe
        """
        def gen_color_segment():
            # 153 == 99
            # 255 == ff
            return random.randint(153, 255)

        while True:
            color = discord.Color.from_rgb(gen_color_segment(), gen_color_segment(), gen_color_segment())

            # prevent white (0xffffff) from being a role color.
            if color.value != 16777215:
                break

        return color