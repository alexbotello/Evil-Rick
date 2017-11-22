import random
import aiohttp
import discord
from discord.ext import commands
from config import logger
from bs4 import BeautifulSoup


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
        search = query.replace(' ', '+')
        url = "http://www.google.com/search?hl=en&safe=off&q="

        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7)' \
                     'Gecko/2009021910 Firefox/3.0.7'
        header = {'User-Agent':user_agent} 
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url + search, headers=header) as resp:
                    if resp.status != 200:
                        raise ValueError()
                    r = await resp.text()
        except ValueError:
            logger.warn(f"{resp.status} response code")
            await ctx.send("Something went wrong you prick? What'd you do?")

        soup = BeautifulSoup(r, 'html.parser')
        for item in soup.find_all('div', {'class': 'g'}):
            href = item.find('a', href=True)['href'].replace('/url?q=', '')
            break
        
        seps = {'%3F': '?' , '%3D': '=', '%2520': '%20'}

        if '&sa' in href:
            link = ''
            for char in href:
                if '&sa' in link:
                    break
                else:
                    link += char
            href = link.replace('&sa', '')

        for key, val in seps.items():
            if key in href:
                href = href.replace(key, val)
        await ctx.send(href)

def setup(bot):
    bot.add_cog(Misc(bot))