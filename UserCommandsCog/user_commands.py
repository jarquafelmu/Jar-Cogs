from redbot.core import commands, app_commands
from difflib import get_close_matches
import discord
import re


class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # users are only allowed to add courses themselves. All courses begin with letters and have numbers
        # Some courses have letters after the numbers, so we need to account for that
        self.courseRegexMatcher = r"[a-z]{2,}\d+([a-z]+)?"

    def isCourse(self, role: str) -> bool:
        """Check if a role is a course."""
        return re.match(self.courseRegexMatcher, role) is not None

    def getRoles(
        self, guild: discord.Guild, roles: list, user, adding: bool = True
    ) -> list:
        """Get a list of qualified roles from the guild. Any roles that do not exist or are not qualified will be skipped."""
        retrievedRoles = []
        for role in roles:
            role = role.lower()
            roleFromGuild = discord.utils.get(guild.roles, name=role)

            # If the role does not exist, skip it
            if roleFromGuild is None:
                continue

            # Only allow users to add or remove courses from themselves
            if self.isCourse(role) is False:
                continue

            # prevent a role from being added that the user already has
            if adding and roleFromGuild in user.roles:
                continue

            # prevent a role from being removed that the user does not have
            if not adding and roleFromGuild not in user.roles:
                continue

            retrievedRoles.append(roleFromGuild)
        return retrievedRoles

    async def send_message(self, message, kwargs):
        """Send a message using context or interactions."""
        if "ctx" in kwargs:
            await kwargs["ctx"].send(message)
        if "interaction" in kwargs:
            await kwargs["interaction"].response.send_message(message, ephemeral=True)

    async def add(
        self,
        user: discord.User,
        guild: discord.Guild,
        roles: str,
        **kwargs,
    ):
        """Generic add method. This is used by the other add commands."""
        role_list = self.getRoles(guild, list(roles.split(" ")), user)

        for role in role_list:
            await user.add_roles(role)

        if not role_list:
            await self.send_message(
                f"Could not find any courses to add. If you feel this is in error, check the spelling of your courses",
                kwargs,
            )
        else:
            await self.send_message(
                f'Added {", ".join([role.name for role in role_list])}.', kwargs
            )

    @commands.command(name="add")
    async def add_command(self, ctx, *, roles: str):
        """Add one or more roles to yourself.

        Example:
        !add role1 role2 role3
        !add role1
        """
        await self.add(ctx.message.author, ctx.guild, roles, ctx=ctx)

    @app_commands.command(name="add", description="Add one or more roles to yourself")
    @app_commands.describe(
        roles="One or more courses to add to yourself. For multiple courses, separate them with spaces"
    )
    @app_commands.rename(roles="courses")
    async def add_app_command(self, interaction: discord.Interaction, roles: str):
        """Slash command to add one or more roles to the user"""
        await self.add(
            interaction.user, interaction.guild, roles, interaction=interaction
        )

    async def remove(
        self,
        user: discord.User,
        guild: discord.Guild,
        roles: str,
        **kwargs,
    ):
        """Generic remove method. This is used by the other remove commands."""
        role_list = self.getRoles(guild, list(roles.split(" ")), user, False)

        for role in role_list:
            await user.remove_roles(role)

        if not role_list:
            await self.send_message(
                f"Could not find any roles to remove. If you feel this is in error, check the spelling for the course.",
                kwargs,
            )
        else:
            await self.send_message(
                f'Removed {", ".join([role.name for role in role_list])}.', kwargs
            )

    @commands.command(name="remove")
    async def remove_command(self, ctx, *, roles: str) -> None:
        """Remove one or more roles from yourself.

        Example:
        !remove role1 role2 role3
        !remove role1
        """
        await self.remove(ctx.message.author, ctx.guild, roles, ctx=ctx)

    @app_commands.command(
        name="remove", description="Add one or more roles to yourself"
    )
    @app_commands.describe(
        roles="One or more courses to remove from yourself. For multiple courses, separate them with spaces"
    )
    @app_commands.rename(roles="courses")
    async def remove_app_command(self, interaction: discord.Interaction, roles: str):
        """Slash command to remove one or more roles from the user"""
        await self.remove(
            interaction.user, interaction.guild, roles, interaction=interaction
        )

    async def search(
        self,
        guild: discord.Guild,
        role: str,
        **kwargs,
    ):
        """Generic search method. This is used by the other search commands."""
        roles = guild.roles
        roles = [
            i for i in roles if self.isCourse(i.name) is True and i.name != "@everyone"
        ]
        role_names = get_close_matches(role, [i.name for i in roles])

        if not role_names:
            await self.send_message(
                f"Could not find any roles close to that name...", kwargs
            )
            return None

        # return the closest 5 matches
        MATCH_LIMIT = 5
        if len(role_names) > MATCH_LIMIT:
            del role_names[MATCH_LIMIT:]

        prettifiedRoles = "\n".join(role_names)
        await self.send_message(
            f"Here are the roles I found close to that name:\n{prettifiedRoles}", kwargs
        )

    @commands.command()
    async def search_command(self, ctx, role):
        """Search for a role by name. If there are multiple matches, you will be shown a list of the closest matches."""
        await self.search(ctx.guild, role, ctx=ctx)

        # TODO: Needs to be rebuilt to no longer use disputils
        # multiple_choice = BotMultipleChoice(ctx, role_names, "Search Results:")
        # choice = await multiple_choice.run()
        # choice = choice[0]
        # if choice:
        #     for i in roles:
        #         if choice == i.name:
        #             choice = i
        #             break
        # else:
        #     await multiple_choice.quit(f"Sorry you did not see the class you were looking for {user.mention}!")
        #     return None
        # await multiple_choice.quit()

        # if choice:
        #     await self.add(ctx, choice)

    @app_commands.command(
        name="search",
        description="Searches for a course and returns a list of up to five matches",
    )
    @app_commands.describe(role="A course you wish to search for")
    @app_commands.rename(role="course")
    async def search_app_command(self, interaction: discord.Interaction, role: str):
        """Search for a role by name. If there are multiple matches, you will be shown a list of the closest matches."""
        await self.search(interaction.guild, role, interaction=interaction)
