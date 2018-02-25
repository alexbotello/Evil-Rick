import asyncio

import discord
from discord.ext import commands

import errors
import settings
from utils.formatter import block
from models import ConcertDatabase
from https import BandsInTownRequest


class Concerts:
    """
    Concert Command Cog
    """
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.bot.loop.create_task(self.finding_concerts())

    @commands.group(invoke_without_command=True)
    async def concert(self, ctx):
        """Concert Finder commands"""
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument

    @concert.command()
    @commands.has_permissions(create_instant_invite=True)
    async def add(self, ctx, *artists):
        """Add artist(s) to search"""
        guild = ctx.guild.name
        with ConcertDatabase(guild) as db:
            db.add_artists(artists)
            await ctx.send("Artists have been added to database")

    @concert.command()
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx, *artists):
        """Remove artist(s) from database"""
        guild = ctx.guild.name
        with ConcertDatabase(guild) as db:
            db.remove_artists(artists)
            await ctx.send("Artists have been removed from database")

    @concert.command(name="list")
    async def _list(self, ctx):
        """List of saved artists"""
        guild = ctx.guild.name
        with ConcertDatabase(guild) as db:
            artists = db.get_artists()
            em = discord.Embed(colour=discord.Colour.default(), title="Saved Artists")
            em.description = block(", ".join(artists))
            await ctx.send(embed=em)

    @concert.command()
    @commands.is_owner()
    async def clean(self, ctx):
        """Cleans the database of old concerts"""
        guild = ctx.guild.name
        with ConcertDatabase(guild) as db:
            items_removed = db.clean_database()
            await ctx.send(f"Removed {items_removed} concerts from database")

    async def finding_concerts(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            concerts = await self.get_concerts()
            await self.post_concert_to_discord(concerts)
            await asyncio.sleep(60 * 120)  # 2 hours

    async def get_concerts(self):
        self.channel = self.generate_channel()
        guild = self.channel.guild.name

        with ConcertDatabase(guild) as db:
            artists = db.get_artists()
            request = BandsInTownRequest(artists=artists)
            await request.send()
            concerts = request.results
            results = db.filter_concerts(concerts)
            return results

    def generate_channel(self):
        return discord.utils.get(self.bot.get_all_channels(),
                                 guild__name='Titty Tavern', name='concerts')

    async def post_concert_to_discord(self, concerts):
        for concert in concerts:
            image = discord.Embed(colour=discord.Colour.default())
            image.set_image(url=concert['thumb'])
            await self.channel.send(embed=image)
            await self.channel.send(concert['title'] + '\n' + concert['fmt_date'])
            await asyncio.sleep(2)


def setup(bot):
    bot.add_cog(Concerts(bot))
