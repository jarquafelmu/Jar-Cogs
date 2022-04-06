from .user_commands import UserCommands


def setup(bot):
    bot.add_cog(UserCommands(bot))