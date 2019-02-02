from redbot.core import commands

import discord
import contextlib


class RoleManager(commands.Cog):
    """Manages roles for Server McServerface"""
    
    guild_id = 493875452046475275
    
    msg_rule_agreement_id = 508393348067885066
    msg_author_id = 513857600152928279
    
    log_id = 509041710651670548
    
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(self.guild_id)
        self.log = self.bot.get_channel(self.log_id)
        
        self.roles = {
            "reader": {
                "id": 506657944860098561
            },
            "author": {
                "id": 506657837498368014
            }
        }
        
        self.roles["reader"]["obj"] = self.guild.get_role(self.roles["reader"]["id"])
        self.roles["author"]["obj"] = self.guild.get_role(self.roles["author"]["id"])
    
    async def on_raw_reaction_add(self, payload):        
        """
        Member agrees to the rules
        """        
        await self.process_reaction(payload, True)
                
    async def on_raw_reaction_remove(self, payload):        
        """
        Member no longer agrees to the rules
        """        
        await self.process_reaction(payload, False)
                
    async def process_reaction(self, payload, add: bool):
        """
        Handles the processing of the reaction
        """
        member = self.guild.get_member(payload.user_id)
        
        if member is None:
            return
        
        print(payload.emoji)
        
        emoji = str(payload.emoji)
        
        print(emoji)
        
        msg_id = payload.message_id
        if msg_id == self.msg_rule_agreement_id:
            await self.process_rule_agreement_reaction(member, emoji, add)
        elif msg_id == self.msg_author_id:
            await self.process_author_reaction(member, emoji, add)           
        
                
    async def process_rule_agreement_reaction(self, member: discord.Member, emoji: str, add: bool):
        """
        Handles the rule agreement reaction
        """        
        
        if emoji.startswith("\N{THUMBS UP SIGN}"):        
            if add:
                msg = (
                    f"Thank you for agreeing to the rules for {member.guild.name}.\n"
                    "You have now been granted access to the server."
                )
                await member.add_roles(self.roles["reader"]["obj"])
            else:
                msg = (
                    f"It is unfortunate that you can no longer agree to the rules for {member.guild.name}.\n"
                    "Your access to the server has been restricted.\n"
                    "If you decide to agree to the rules in the future, your access will be restored."
                )
                await member.remove_roles(self.roles["reader"]["obj"])
            
            with contextlib.suppress(discord.HTTPException):
                # we don't want blocked DMs preventing the function working
                await member.send(msg)
            
        
                
    async def process_author_reaction(self, member: discord.Member, emoji: str, add: bool):
        """
        Handles the rule agreement reaction
        """
        
        if emoji.startswith("\N{LOWER LEFT BALLPOINT PEN}"):
            if add:
                await member.add_roles(self.roles["author"]["obj"])
            else:
                await member.remove_roles(self.roles["author"]["obj"])
