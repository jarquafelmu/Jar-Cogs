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
        
        # channels
        self.channel_courseList = None
        self.channel_log = None
        self.channel_newMembers = None
        self.channel_welcome = None


    @property
    def courseList(self):
        """
        Course List channel object
        """
        if self.channel_courseList is None:
            self.channel_courseList = self.bot.get_channel(self.channel_ids["courseList"])
        return self.channel_courseList

    @property
    def log(self):
        """
        Logging channel object
        """
        if self.channel_log is None:
            self.channel_log = self.bot.get_channel(self.channel_ids["log"])
        return self.channel_log
    @property
    def newMembers(self):
        """
        New Members channel object
        """
        if self.channel_newMembers is None:
            self.channel_newMembers = self.bot.get_channel(self.channel_ids["newMembers"])
        return self.channel_newMembers

    @property
    def welcome(self):
        """
        Server Guidelines channel object
        """
        if self.channel_welcome is None:
            self.channel_welcome = self.bot.get_channel(self.channel_ids["welcome"])
        return self.channel_welcome

    def anchor(self, channel):
        """
        Formats the channel for embedding in a string
        """
        return f"<#{channel}>"