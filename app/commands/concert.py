import json
import datetime
import pymongo
import discord
import aiohttp
import asyncio
import settings
from discord.ext import commands
from commands.utils.formatter import block
from config import logger, ConnectDatabase


class Concerts:
    """
    Concert Command Cog
    """
    def __init__(self, bot):
        self.bot = bot
        self.api = '2.0'
        self._artists = None
        self._radius = settings.RADIUS
        self._location = settings.LOCATION
        self.id = settings.ID
        self._url = settings.BIT_URL
        self.bot.loop.create_task(self.concert_finder()) # Concert Scraper Background Task
 
    def load_artists(self, ctx, db):
        try:
            query = db.find_one({"id": ctx.guild.id})
            if query:
                return [a for a in query['artists']]
            else:
                return None
        except pymongo.errors.OperationFailure:
            logger.error("Could not retrieve artists from database..")
        
    async def concert_finder(self):
        """
        Main control loop for request
        """
        await self.bot.wait_until_ready()

        channel = discord.utils.get(self.bot.get_all_channels(), 
                        guild__name='Titty Tavern', name='concerts')
        
        while not self.bot.is_closed():
            with ConnectDatabase(channel.guild.name) as db:
                if self._artists is None:
                    self._artists = self.load_artists(channel, db)
                all_concerts = await self.find_all_concerts(db)

            for concert in all_concerts:
                image = discord.Embed(colour=discord.Colour.default())
                image.set_image(url=concert['image'])
                await channel.send(embed=image)
                await channel.send(concert['title'] + '\n' + concert['date'])
                await asyncio.sleep(2)
            await asyncio.sleep(60 * 300) # 5 Hours
    
    async def find_all_concerts(self, db):
        """
        Use BandsinTown API to search for concert events
        """
        results = []
        self.date = datetime.datetime.now().isoformat()
        
        for artist in self._artists:
            URL = self._url + artist + '/events/search'

            param = {'app_id': settings.ID, 'api_version': self.api,
                    'location': self._location, 'radius': self._radius,
                    'format': 'json'}
            async with aiohttp.ClientSession() as session:
                async with session.get(URL, params=param) as resp:
                    if resp.status != 200:
                        raise ValueError(f'{resp.status} response code')
                    json_data = await resp.json()

                    old_result_found = 0
                    new_results_found = 0
                    for event in json_data:
                        concert = db.find_one({'_id': event['id']})
                        if concert:
                            if concert['datetime'] < self.date:
                                try:
                                    db.delete_one(concert)
                                except pymongo.errors.OperationFailure:
                                    logger.error('Error removing outdated concert from database...')
                            else:
                                old_result_found += 1
                        else:
                            concert = {
                                "_id": event['id'],
                                "title": event['title'],
                                "date": event['formatted_datetime'],
                                'artist': event['artists'][0]['name'],
                                'image': event['artists'][0]['image_url'],
                                'datetime': event['datetime']
                            }
                            try:
                                db.insert_one(concert)
                                new_results_found += 1
                                results.append(concert)
                            except pymongo.errors.OperationFailure:
                                logger.error('Error inserting concert into database...')
            if json_data:
                logger.info(f'Found {old_result_found} posted result and ' 
                            f'{new_results_found} new results for {artist}')
            else:
                logger.info(f"Found No Results for {artist}")

        logger.info(f'Concert Scrape Completed: {datetime.datetime.now().isoformat()}')
        return results

    @commands.group(invoke_without_command=True)
    async def concert(self, ctx):
        """
        Concert Finder commands
        """
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument

    @concert.command()
    async def info(self, ctx):
        """
        Displays the location and radius info
        """
        await ctx.send(f"Searching a {self._radius} mile radius around {self._location} for concerts")
    
    @concert.command()
    @commands.has_permissions(create_instant_invite=True)
    async def add(self, ctx, *artists):
        """
        Add artist(s) to search
        """
        items = []
        with ConnectDatabase(ctx.guild.name) as db:
            self._artists = self.load_artists(ctx, db)        
        
        for artist in artists:
            try:
                if artist in self._artists:
                    await ctx.send(f'{artist} is already saved...')
            except TypeError:
                items.append(artist)
            else:
                items.append(artist)
        
        with ConnectDatabase(ctx.guild.name) as db:
            document = db.find_one({'id': ctx.guild.id})
            
            if document:
                self._artists = self._artists + items
                db.update_one({'id': ctx.guild.id}, {"$set": {'artists': self._artists}})
                await ctx.send(f"{items} has been added")
            else:
                self._artists = items
                artists = {"id": ctx.guild.id, "artists": items}   
                db.insert_one(artists)
                await ctx.send(f"{items} has been added")
    
    @concert.command()
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx, *artists):
        """
        Remove artist(s) from database
        """
        with ConnectDatabase(ctx.guild.name) as db:
            self._artists = self.load_artists(ctx, db)
            
            typos = list(set(artists).difference(self._artists))
            values = list(set(artists).intersection(self._artists))
            self._artists = list(set(self._artists).difference(artists))            
            
            db.update_one({'id': ctx.guild.id}, {"$set": {'artists': self._artists}})
        
        if typos and not values:
            await ctx.send(f"{typos} is not in list. Typo?")
        elif typos and values:
            logger.error(f"Values: {values}")
            await ctx.send(f"{values} has been removed\n{typos} is not in list. Typo?")
        else:
            await ctx.send(f"{values} has been removed from list")

    @concert.command(hidden=True)
    @commands.is_owner()
    async def location(self, ctx, location):
        """
        Changes the search location
        """
        self._location = location
        await ctx.send(f"Location setting has been changed to {self._location}")
    
    @concert.command(hidden=True)
    @commands.is_owner()
    async def radius(self, ctx, radius: int):
        """
        Changes the search radius
        """
        self._radius = str(radius) if radius <= 150 else '150'
        await ctx.send(f"Radius setting has been changed to {self._radius}")
        
    @concert.command(name="list")
    async def _list(self, ctx):
        """
        List of saved artists
        """
        with ConnectDatabase(ctx.guild.name) as db:
            self._artists = self.load_artists(ctx, db)
        
        if self._artists is None:
            await ctx.send("You have no saved artists, use '?concert add <artist>' to add")
        else:
            em = discord.Embed(colour=discord.Colour.default(), title="Saved Artists")
            em.description = block(", ".join(self._artists))
            await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Concerts(bot))