from redbot.core import commands
from .logic import Logic
from .logger import logger
import discord
import random

class RoleHandler(commands.Cog):
    def __init__(self, bot, args):
        """
        Initialize the CourseAssignment object
        """
        self.bot = bot
        self.logic = args["logic"]
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
        createRole = await self.logic.confirm(ctx, msg=f"Role `{role_name}` does not exist. Would you like to create it?")
        if (createRole):
            color = self.get_role_color()
            try:
                # create the role in the guild
                role_obj = await ctx.guild.create_role(name=role_name, color=color)
            except discord.InvalidArgument:
                logger.exception("InvalidArgument")
            except discord.Forbidden:
                logger.exception(f"Bot lacks permission to add roles to the server.")
            except discord.HTTPException:
                logger.exception(f"Creating the role failed.")
            else:
                logger.info(f"Creating role for {role_name}.")
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

    async def update_member(self, member: discord.Member, role: discord.Role, add: bool):
        """
        Handles the rule agreement reaction.
        """
        if add:
            await member.add_roles(role)
            action = "added"
        else:
            await member.remove_roles(role)
            action = "removed"
        logger.debug(f"{action} role: {role.name} to member: {member.name}")
        pass