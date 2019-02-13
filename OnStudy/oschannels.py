from redbot.core import commands


class OSChannels(commands.Cog):
    """
    Enum for channels to make it simplier to access them when needed
    """    

    course_list_id = 514518408122073116
    log_id = 485218362272645120
    new_members_id = 484378858968055814
    roles_id = 482361038478508034
    welcome_id = 514572072794587136

    def __init__(self, bot):
        self.bot = bot

    @property
    def courseList(self):
        """
        Course List channel object
        """
        return self.bot.get_channel(self.course_list_id)

    @property
    def log(self):
        """
        Logging channel object
        """
        return self.bot.get_channel(self.log_id)

    @property
    def newMembers(self):
        """
        New Members channel object
        """
        return self.bot.get_channel(self.new_members_id)

    @property
    def roles(self):
        """
        Roles channel object
        """
        return self.bot.get_channel(self.roles_id)

    @property
    def welcome(self):
        """
        Server Guidelines channel object
        """
        return self.bot.get_channel(self.welcome_id)

    def anchor(self, channel):
        """
        Formats the channel for embedding in a string
        """
        return f"<#{channel}>"