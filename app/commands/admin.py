from discord.ext import commands
from commands.utils import checks
import discord


class Admin:
    """Admin and moderator utility commands"""
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member):
        """Kick A Selected Member"""
        initiator = ctx.message.author.name

        try:
            await self.bot.kick(member)
            await self.bot.say(f"{member.name} was kicked by {initiator}")
        except discord.Forbidden:
            await self.bot.say("You do not have permission to use this command")


    @commands.command(pass_context=True, no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member):
        """Ban A Selected Member"""
        initiator = ctx.message.author.name
        self.ban_list[member.name] = member.id
        
        try:
            await self.bot.ban(member)
            await self.bot.say(f"{member.name}'s been banished to the shadow realm by {initiator}")
        except discord.Forbidden:
            await self.bot.say("You do not have permission to use this command")

    @commands.command(pass_context=True, no_pm=True)   
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member):
        """ Unbans A Selected Member """
        initiator = ctx.message.author.name
        banned_users = await self.bot.get_bans(ctx.message.server)

        for user in banned_users:
            if member == user.name:
                member = user

        try:
            await self.bot.unban(ctx.message.server, member)
            await self.bot.say(f"{member} has been reprieved by {initiator}")
        except discord.Forbidden:
            await self.bot.say("You do not have permission to use this command")
    

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_permissions(kick_members=True)
    async def delete(self, ctx, num: int):
        """Delete a specified number of messages"""
        number = num or 100
        try:
            await self.bot.purge_from(ctx.message.channel, limit=number)
            await self.bot.say(f"Deleted {number} messages from channel")
        except discord.HTTPException:
            await self.bot.say("You can only bulk delete messages that "
                               "are under 14 days old")


    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def invite(self, ctx):
        """Create an instant invite"""
        invite = await self.bot.create_invite(ctx.message.channel,
                                              max_uses=5, max_age=5)

        await self.bot.delete_message(ctx.message)
        await self.bot.say(invite)


    @commands.command(pass_context=True)
    @commands.has_permissions(manage_messages=True)
    async def joined_at(self, ctx, member: discord.Member = None):
        """Display Member Join Date"""
        if member is None:
            member = ctx.message.author
        await self.bot.say('{member.name} joined at {member.joined_at}')


def setup(bot):
    bot.add_cog(Admin(bot))
