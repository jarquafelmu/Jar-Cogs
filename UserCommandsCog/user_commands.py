from redbot.core import commands
from difflib import get_close_matches
import discord
import re

class UserCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        # users are only allowed to add courses themselves. All courses begin with letters and have numbers
        # Some courses have letters after the numbers, so we need to account for that
        self.courseRegexMatcher = r'[a-zA-Z]{2,}\d+([a-zA-Z]+)?'
        
        # old permission number
        # self.perm_num = 1071698665025
        
    def isCourse(self, role: str) -> bool:
        """Check if a role is a course."""
        return re.match(self.courseRegexMatcher, role) is not None
        
    def getRoles(self, ctx, roles: list, user, adding: bool = True) -> list:
        """Get a list of qualified roles from the guild. Any roles that do not exist or are not qualified will be skipped."""
        retrievedRoles = []
        for role in roles:
            roleFromGuild = discord.utils.get(ctx.guild.roles, name=role)
            
            # If the role does not exist, skip it
            if roleFromGuild is None:
                continue
            
            # Only allow users to add or remove courses from themselves
            if(self.isCourse(role) is False):
                continue
            
            # prevent a role from being added that the user already has
            if (adding and roleFromGuild in user.roles):
                continue

            # prevent a role from being removed that the user does not have
            if (not adding and roleFromGuild not in user.roles):
                continue
            
            retrievedRoles.append(roleFromGuild)
        return retrievedRoles
    
    @commands.command()
    async def add(self, ctx, *, roles: str):
        """Add one or more roles to yourself.

        Example: 
        !add role1 role2 role3
        !add role1
        """
        user = ctx.message.author
        role_list = self.getRoles(ctx, list(roles.split(" ")), user)
        
        for role in role_list: 
            await user.add_roles(role)
            
        if not role_list:
            await ctx.send(f'Could not find any roles to add {user.mention}')
        else:
            await ctx.send(f'Added {", ".join([role.name for role in role_list])} to {user.mention}')

    @commands.command()
    async def remove(self, ctx, *, roles: str) -> None:
        """Remove one or more roles from yourself.

        Example: 
        !remove role1 role2 role3
        !remove role1
        """        
        user = ctx.message.author
        role_list = self.getRoles(ctx, list(roles.split(" ")), user, False)
        
        for role in role_list: 
            await user.remove_roles(role)
            
        if not role_list:
            await ctx.send(f'Could not find any roles to remove {user.mention}')
        else:
            await ctx.send(f'Removed {", ".join([role.name for role in role_list])} to {user.mention}')

    @commands.command()
    async def search(self, ctx, role):
        """Search for a role by name. If there are multiple matches, you will be shown a list of the closest matches.
        """
        user = ctx.message.author
        roles = ctx.guild.roles
        roles = [i for i in roles if self.isCourse(i.name) is True and i.name != '@everyone']
        role_names = get_close_matches(role, [i.name for i in roles])

        if not role_names:
            await ctx.send(f"Could not find any roles close to that name... {user.mention}")
            return None
        # return the closest 5 matches
        MATCH_LIMIT = 5
        if len(role_names) > MATCH_LIMIT:
            del role_names[MATCH_LIMIT:]


        prettifiedRoles = '\n'.join(role_names)
        await ctx.send(f"Here are the roles I found close to that name {user.mention}:\n{prettifiedRoles}")
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
