import random

import discord
from discord.ext import commands

from utils.google import GoogleSearch
from utils.reddit import Reddit


class Misc:
    """
    Misc Command Cog
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 20.0, type=commands.BucketType.guild)
    async def roll(self, ctx):
        """
        Rolls the dice
        """
        value = random.randrange(0, 101)
        user = ctx.author.display_name
        await ctx.send(f"{user}: **{value}**")

    @commands.command()
    @commands.cooldown(1, 3.0, type=commands.BucketType.guild)
    async def g(self, ctx, *, query):
        """
        Feeling lucky? Returns first result from google
        """
        result = await GoogleSearch(query)()
        await ctx.send(result)
    
    @commands.command()
    @commands.cooldown(1, 30.0, type=commands.BucketType.guild)
    async def troll(self, ctx, *, member : discord.Member):
        """
        Dadbod requested it...
        """
        reddit = Reddit(subreddit="ladybonersgw")
        links = await reddit()

        await ctx.send(f"*trolls {member.display_name}*")
        [await member.send(content=link) for link in links]
        await member.send(f"**You've been trolled by {ctx.author.display_name}**")


def setup(bot):
    bot.add_cog(Misc(bot))
