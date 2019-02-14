from redbot.core import commands


class OSChannels(commands.Cog):
    """
    Enum for channels to make it simplier to access them when needed
    """    
    channel_ids = {        
        "courseList": 514518408122073116,
        "log": 485218362272645120,
        "newMembers": 484378858968055814,
        "welcome": 514572072794587136
    }

    def __init__(self, bot):
        self.bot = bot

    @property
    def courseList(self):
        """
        Course List channel object
        """
        if self.courseList is None:
            self.courseList = self.bot.get_channel(self.channel_ids["courseList"])
        return self.courseList

    @property
    def log(self):
        """
        Logging channel object
        """
        if self.log is None:
            self.log = self.bot.get_channel(self.channel_ids["log"])
        return self.log
    @property
    def newMembers(self):
        """
        New Members channel object
        """
        if self.newMembers is None:
            self.newMembers = self.bot.get_channel(self.channel_ids["newMembers"])
        return self.newMembers

    @property
    def welcome(self):
        """
        Server Guidelines channel object
        """
        if self.welcome is None:
            self.welcome = self.bot.get_channel(self.channel_ids["welcome"])
        return self.welcome

    def anchor(self, channel):
        """
        Formats the channel for embedding in a string
        """
        return f"<#{channel}>"