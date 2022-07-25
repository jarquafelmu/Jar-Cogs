from redbot.core import commands
import discord
from difflib import get_close_matches
from disputils import BotMultipleChoice

class UserCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.perm_num = 1071698665025

    @commands.command(name="add")
    async def add(self, ctx, role: discord.Role):
        user = ctx.message.author
        if role is None:
            await ctx.send(f'That role dose not exist {user.mention}')
        elif role.permissions.value != self.perm_num:
            await ctx.send(f'You do not have permission to add this role')
        elif role in user.roles:
            await ctx.send(f"You cannot add a role you already have {user.mention}")
        else:
            user = ctx.message.author
            await user.add_roles(role)
            await ctx.send(f'Added {role} to {user.mention}')

    @commands.command(name="remove")
    async def remove(self, ctx, role) -> None:
        role = discord.utils.get(ctx.guild.roles, name=role)
        user = ctx.message.author
        if role is None:
            await ctx.send(f'That role dose not exist {user.mention}')
        elif role.permissions.value != self.perm_num:
            await ctx.send('You do not have permission to remove this role')
        elif role not in user.roles:
            await ctx.send(f"You cannot remove a role you don't have {user.mention}")
        else:
            await user.remove_roles(role)
            await ctx.send(f"Removed {role} from {user.mention}")

    @commands.command(name="search")
    async def search(self, ctx, role):
        user = ctx.message.author
        roles = ctx.guild.roles
        roles = [i for i in roles if i.permissions.value == self.perm_num and i.name != '@everyone']
        role_names = get_close_matches(role, [i.name for i in roles])

        if not role_names:
            await ctx.send(f"Could not find any roles close to that name... {user.mention}")
            return None
        if len(role_names) > 5:
            del role_names[5:]


        multiple_choice = BotMultipleChoice(ctx, role_names, "Search Results:")
        choice = await multiple_choice.run()
        choice = choice[0]
        if choice:
            for i in roles:
                if choice == i.name:
                    choice = i
                    break
        else:
            await multiple_choice.quit(f"Sorry you did not see the class you were looking for {user.mention}!")
            return None
        await multiple_choice.quit()

        if choice:
            await self.add(ctx, choice)

def setup(bot):
    bot.add_cog(UserCommands(bot))
