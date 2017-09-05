from discord.ext import commands
from commands.utils.formatter import block
from commands.utils import checks
from config import logger
import pymongo
import discord
import requests
import asyncio
import json
import time
import settings


class Concerts:
    """Concert Display Commands"""
    # TODO AUTO CLEAN THE DATABASE TO REMOVE CONCERT DATES THAT HAVE ALREADY HAPPENED
    # TODO REMOVE ARTISTS COMMAND
    def __init__(self, bot):
        self.bot = bot
        self.api = '2.0'
        self._client = pymongo.MongoClient(settings.DB_URL)
        self._db = None
        self._artists = None
        self._radius = settings.RADIUS
        self._location = settings.LOCATION
        self.id = settings.ID
        self._url = settings.BIT_URL
 
    def connect_database(self, server):
        db = self._client.setting.DB_NAME
        return db[server.name]
    
    def load_artists(self, server):
        self._db = self.connect_database(server)
        query = self._db.find_one({"id": server.id})
        if query:
            self._client.close()
            return [a for a in query['artists']]
        else:
            self._client.close()
            return None
    
    def _verify_database_integrity(self):
        pass

    async def concert_finder(self, ctx):
        """Loop that scrapes concert data"""
        channel = ctx.message.channel
        while not self.bot.is_closed:
            all_concerts = self.find_all_concerts(ctx)
            for concert in all_concerts:
                image = discord.Embed(colour=discord.Colour.default())
                image.set_image(url=concert['image'])
                await self.bot.send_message(channel, embed=image)
                await self.bot.send_message(channel, concert['title'] + '\n' + concert['date'])
                await asyncio.sleep(2)
            #await asyncio.sleep(60 * 500)
            await asyncio.sleep(30)
    
    def find_all_concerts(self, ctx):
        """
        Use BandsinTown API to search for concert events
        """
        if self._artists is None:
            self._artists = self.load_artists(ctx.message.server)
        if self._db is None:
            self._db = self.connect_database(ctx.message.server)
       
        concerts = self._db
        results = []

        for artist in self._artists:
            URL = self._url + artist + '/events/search'

            param = {'app_id': settings.ID, 'api_version': self.api,
                    'location': self._location, 'radius': self._radius,
                    'format': 'json'}
            resp = requests.get(URL, params=param)
            if resp.status_code != 200:
                raise ValueError(f'{resp.status_code} response code')
            # Load JSON data from response
            json_data = json.loads(resp.text)

            old_result_found = 0
            new_results_found = 0
            for event in json_data:
                concert = concerts.find_one({'_id': event['id']})
                if concert:
                    old_result_found += 1
                else:
                    concert = {
                        "_id": event['id'],
                        "title": event['title'],
                        "date": event['formatted_datetime'],
                        'artist': event['artists'][0]['name'],
                        'image': event['artists'][0]['image_url']
                    }
                    concerts.insert_one(concert)
                    new_results_found += 1
                    results.append(concert)

            if json_data == []:
                logger.info(f'Found No Results For {artist}')
            if json_data:
                logger.info(f'Found {old_result_found} posted result and ' 
                            f'{new_results_found} new results for {artist}')
        logger.info("Scrape was completed")
        self._client.close()
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
        server = ctx.message.server
        if self._db is None:
            self._db = self.connect_database(server)
        await self.concert_finder(ctx)
    
    @concert.command(pass_context=True)
    async def info(self, ctx):
        """Displays the location and radius of search"""
        await self.bot.say(f"Searching a {self._radius} mile radius around {self._location} for concerts")

    @concert.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def add(self, ctx, *artists):
        """Add artist(s) to look for"""
        guild = ctx.message.server
        items = []
        
        if self._artists is None:
            self._artists = self.load_artists(guild)        
        if self._db is None:
            self._db = self.connect_database(guild)
        
        #TODO TURN THIS INTO LIST COMPREHENSION OR CONDENSE IT 
        for artist in artists:
            artist = artist.replace("_", " ")
            try:
                if artist in self._artists:
                    await self.bot.say(f'{artist} is already saved...')
                    return
            except TypeError:
                items.append(artist)
            else:
                items.append(artist)
        
        document = self._db.find_one({'id': guild.id})
        if document:
            self._artists = self._artists + items
            self._db.update({'id': guild.id}, {"$set": {'artists': self._artists}})
            await self.bot.say(f"{items} have been added")
        else:
            self._artists = items
            artists = {"id": guild.id, "artists": items}   
            self._db.insert_one(artists)
            await self.bot.say(f"{items} have been added")
        self._client.close()
    
    @concert.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx, *artists):
        """Remove artist(s) from list"""
        guild = ctx.message.server
        if self._artists is None:
            self._artists = self.load_artists(guild)
        if self._db is None:
            self._db = self.connect_database(guild)
       
        self._artists = [a for a in self._artists if not (a in artists)]
        self._db.update({'id': guild.id}, {"$set": {'artists': self._artists}})
        await self.bot.say(f"{artists} has been removed")
        self._client.close()

    @concert.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def location(self, ctx, location):
        """Changes location of search"""
        self._location = location
        await self.bot.say(f"Location setting has been changed to {self._location}")
    
    @concert.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def radius(self, ctx, radius):
        """Changes the search radius"""
        self._radius = radius
        await self.bot.say(f"Radius setting has been changed to {self._radius}")
        
    @concert.command(pass_context=True, name="list")
    async def _list(self, ctx):
        """List your saved artists"""
        guild = ctx.message.server
        self._artists = self.load_artists(guild)
        if self._artists is None:
            await self.bot.say("You have no saved artists, use '?concert add <artist>' to add")
        else:
            em = discord.Embed(colour=discord.Colour.default(), title="Saved Artists")
            em.description = block(", ".join(self._artists))
            await self.bot.send_message(ctx.message.channel, embed=em)

def setup(bot):
    bot.add_cog(Concerts(bot))