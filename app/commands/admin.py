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
        initiator = ctx.message.author

        await self.bot.delete_message(ctx.message)
        await self.bot.kick(member)
        await self.bot.say("```{} was kicked by {}```".format(member, initiator))


    @commands.command(pass_context=True, no_pm=True)
    @commands.has_permissions(ban_members=True)
    @checks.is_owner()
    async def ban(self, ctx, member: discord.Member):
        """Ban A Selected Member"""
        initiator = ctx.message.author

        await self.bot.delete_message(ctx.message)
        await self.bot.ban(member)
        await self.bot.say("```{}'s been banished "
                           "to the shadow realm by {}```".format(member,
                                                                 initiator))

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_permissions(ban_members=True)
    @checks.is_owner()
    async def unban(self, ctx, member: discord.Member):
        """ Unbans A Selected Member """
        initiator = ctx.message.author
        await self.bot.delete_message(ctx.message)

        try:
            await self.bot.unban(ctx.message.server, member)
            await self.bot.say("```{} has been reprieved by {}".format(member,
                                                                   initiator))
        except discord.Forbidden:
            await ctx.author.send("Your privilege is too low to issue this "
                                  "commands")


    @commands.command(pass_context=True, no_pm=True)
    @commands.has_permissions(kick_members=True)
    async def delete(self, ctx, num: int):
        """Delete a specified number of messages"""
        number = num or 100
        try:
            await self.bot.purge_from(ctx.message.channel, limit=number)
            await self.bot.say("```Deleted {} messages "
                               "from channel```".format(number))
        except discord.HTTPException:
            await self.bot.say("```You can only bulk delete messages that "
                               "are under 14 days old```")


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
        await self.bot.say('```{0} joined at {1}```'.format(member, member.joined_at))


def setup(bot):
    bot.add_cog(Admin(bot))
