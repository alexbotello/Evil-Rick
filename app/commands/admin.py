import discord
from discord.ext import commands
from config import logger


class Admin:
    """Admin and moderator utility commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member):
        """Kick A Selected Member"""
        try:
            await ctx.guild.kick(member)
            await ctx.send(f"{member.name} was kicked by {ctx.author.display_name}")
        except discord.Forbidden:
            await ctx.send("You do not have permission to use this command")


    @commands.command(no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member):
        """Ban A Selected Member"""
        try:
            await ctx.guild.ban(member)
            await ctx.send(f"{member.name}'s been banished to the shadow realm by {ctx.author.display_name}")
        except discord.Forbidden:
            await ctx.send("You do not have permission to use this command")

    @commands.command(no_pm=True)   
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member):
        """ Unbans A Selected Member """
        banned_users = await ctx.guild.bans()
        for user in banned_users:
            if member == user[1].name:
                member = user[1]
        try:
            await ctx.guild.unban(member)
            await ctx.send(f"{member.name} has been reprieved by {ctx.author.display_name}")
        except discord.Forbidden:
            await ctx.send("You do not have permission to use this command")    

    @commands.command(no_pm=True)
    @commands.has_permissions(kick_members=True)
    async def delete(self, ctx, num: int):
        """Delete a specified number of messages"""
        num += 1
        try:
            await ctx.channel.purge(limit=num)
            await ctx.author.send(f"Deleted {num} messages from {ctx.channel}")
        except discord.HTTPException:
            await ctx.send("You can only bulk delete messages that "
                               "are under 14 days old")
        except discord.Forbidden:
            await ctx.send("You do not have permission to use this command")


    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    async def invite(self, ctx):
        """Create an instant invite"""
        invite = await ctx.channel.create_invite(max_age=0, max_uses=2)
        await ctx.message.delete()
        await ctx.send(invite)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def joined_at(self, ctx, member: discord.Member = None):
        """Display Member Join Date"""
        if member is None:
            member = ctx.author
        await ctx.send(f'{member.display_name} joined at {member.joined_at}')


def setup(bot):
    bot.add_cog(Admin(bot))
