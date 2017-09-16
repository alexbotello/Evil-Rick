import json
import datetime
import requests
import pymongo
import discord
import asyncio
import settings
from discord.ext import commands
from commands.utils import checks
from commands.utils.formatter import block
from config import logger, connect_database


class Concerts:
    """Concert Display Commands"""
    def __init__(self, bot):
        self.bot = bot
        self.api = '2.0'
        self._artists = None
        self.is_running = False
        self._radius = settings.RADIUS
        self._location = settings.LOCATION
        self.id = settings.ID
        self._url = settings.BIT_URL
 
    def load_artists(self, db, server):
        try:
            query = db.find_one({"id": server.id})
            if query:
                return [a for a in query['artists']]
            else:
                return None
        except pymongo.errors.OperationFailure:
            logger.error("Could not retrieve artists from database..")
        
    async def concert_finder(self, ctx):
        """Loop that scrapes concert data"""
        channel = ctx.message.channel
        guild = ctx.message.server
        while not self.bot.is_closed:
            self.is_running = True
            with connect_database(guild.name) as db:
                all_concerts = await self.find_all_concerts(ctx, db)
            for concert in all_concerts:
                image = discord.Embed(colour=discord.Colour.default())
                image.set_image(url=concert['image'])
                await self.bot.send_message(channel, embed=image)
                await self.bot.send_message(channel, concert['title'] + '\n' + concert['date'])
                await asyncio.sleep(2)
            #await asyncio.sleep(60 * 500)
            await asyncio.sleep(30)
    
    async def find_all_concerts(self, ctx, db):
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
            resp = requests.get(URL, params=param)
            if resp.status_code != 200:
                raise ValueError(f'{resp.status_code} response code')
            json_data = json.loads(resp.text)

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

            if json_data == []:
                logger.info(f'Found No Results For {artist}')
            if json_data:
                logger.info(f'Found {old_result_found} posted result and ' 
                            f'{new_results_found} new results for {artist}')
        logger.info("Scrape was completed")
        return results

    @commands.group(invoke_without_command=True, pass_context=True)
    async def concert(self, ctx):
        """Concert related commands"""
        if ctx.invoked_subcommand is None:
            raise commands.MissingRequiredArgument

    @concert.command(pass_context=True, hidden=True)
    @commands.has_permissions(ban_members=True)
    async def start(self, ctx):
        """Start Concert Finder"""
        guild = ctx.message.server
        with connect_database(guild.name) as db:
            self._artists = self.load_artists(db, guild)
        if self._artists is None:
            await self.bot.say("Please add artists first using '?concert add <artists>'")
        else:
            await self.concert_finder(ctx)
    
    @concert.command(pass_context=True)
    async def info(self, ctx):
        """Displays the location and radius of search"""
        await self.bot.say(f"Searching a {self._radius} mile radius around {self._location} for concerts")
    
    @concert.command(pass_context=True)
    async def status(self, ctx):
        """The current status of loop"""
        await self.bot.say(f"Loop status: {self.is_running}")

    @concert.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def add(self, ctx, *artists):
        """Add artist(s) to look for"""
        guild = ctx.message.server
        items = []

        with connect_database(guild.name) as db:
            self._artists = self.load_artists(db, guild)        
        
        #TODO TURN THIS INTO LIST COMPREHENSION OR CONDENSE IT
        for artist in artists:
            try:
                if artist in self._artists:
                    await self.bot.say(f'{artist} is already saved...')
            except TypeError:
                items.append(artist)
            else:
                items.append(artist)
        
        with connect_database(guild.name) as db:
            document = db.find_one({'id': guild.id})
            if document:
                self._artists = self._artists + items
                db.update_one({'id': guild.id}, {"$set": {'artists': self._artists}})
                await self.bot.say(f"{items} has been added")
            else:
                self._artists = items
                artists = {"id": guild.id, "artists": items}   
                db.insert_one(artists)
                await self.bot.say(f"{items} has been added")
    
    @concert.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx, *artists):
        """Remove artist(s) from list"""
        guild = ctx.message.server
        
        with connect_database(guild.name) as db:
            self._artists = self.load_artists(db, guild)
            
            typos = list(set(artists).difference(self._artists))
            values = list(set(artists).intersection(self._artists))
            self._artists = list(set(self._artists).difference(artists))            
            
            db.update_one({'id': guild.id}, {"$set": {'artists': self._artists}})
        
        if values == [] and typos:
            await self.bot.say(f"{typos} is not in list. Typo?")
        elif typos and values != []:
            logger.error(f"Values: {values}")
            await self.bot.say(f"{values} has been removed\n{typos} is not in list. Typo?")
        else:
            await self.bot.say(f"{values} has been removed from list")

    @concert.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def location(self, ctx, location):
        """Changes location of search"""
        self._location = location
        await self.bot.say(f"Location setting has been changed to {self._location}")
    
    @concert.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def radius(self, ctx, radius: int):
        """Changes the search radius"""
        self._radius = str(radius) if radius <= 150 else '150'
        await self.bot.say(f"Radius setting has been changed to {self._radius}")
        
    @concert.command(pass_context=True, name="list")
    async def _list(self, ctx):
        """List your saved artists"""
        guild = ctx.message.server

        with connect_database(guild.name) as db:
            self._artists = self.load_artists(db, guild)
        
        if self._artists is None:
            await self.bot.say("You have no saved artists, use '?concert add <artist>' to add")
        else:
            em = discord.Embed(colour=discord.Colour.default(), title="Saved Artists")
            em.description = block(", ".join(self._artists))
            await self.bot.send_message(ctx.message.channel, embed=em)

def setup(bot):
    bot.add_cog(Concerts(bot))
    