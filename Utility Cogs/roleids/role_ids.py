from redbot.core import commands


class RoleIds(commands.Cog):
    """Retreives a list of server roles and their ids"""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def getIds(self, ctx):
        """displays a list of server roles and their ids"""
        
        async with ctx.channel.typing():
            for role in ctx.guild.roles:
                await ctx.channel.send(f"{role.name}: {role.id}")
