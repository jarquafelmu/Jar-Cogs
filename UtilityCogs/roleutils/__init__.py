from .role_utils import RoleUtils


async def setup(bot):
    cog = RoleUtils(bot)
    await bot.add_cog(cog)
