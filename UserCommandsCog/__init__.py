from .user_commands import UserCommands


async def setup(bot):
    await bot.add_cog(UserCommands(bot))