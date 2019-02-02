from .role_ids import RoleIds


async def setup(bot):
    cog = RoleIds(bot)
    bot.add_cog(cog)
