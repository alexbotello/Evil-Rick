import pymongo
import discord
import settings
from discord.ext import commands
from commands.utils.formatter import block
from config import logger, ConnectDatabase
from commands.utils import checks, paginator



class Tags:
    """ Tag related commands for Cocobot """

    def __init__(self, bot):
        self.bot = bot
        #self.paginator = commands.Paginator(max_size=99)

    @commands.group(invoke_without_command=True, pass_context=True)
    async def tag(self, ctx, *, name):
        """ Retrieve a tag command from the server """
        guild = ctx.message.server.id
       
        with ConnectDatabase(guild) as db:
            tags = db
            tag = tags.find_one({"name": name}) 
    
        if tag is None:
            await self.bot.say('No tag was found...')
        else:
            content = tag['content']
            await self.bot.say(content)
        
    @tag.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def create(self, ctx, name, *, content):
        """ Create a new tag for the server """
        guild = ctx.message.server.id
        
        with ConnectDatabase(guild) as db:
            tag = db.find_one({"name": name})
            if tag:
                await self.bot.say("Tag already exists...")
            else:
                tag = { "name": name,
                        "content": content,
                        "creator": ctx.message.author.name
                }
                db.insert_one(tag)

                msg = f"'?tag {tag['name']}' has been created by {tag['creator']}"
                await self.bot.delete_message(ctx.message)
                await self.bot.say(block(msg))
            
    @tag.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx, *, name):
        """ Remove specified tag from server """
        guild = ctx.message.server.id
        
        with ConnectDatabase(guild) as db:
            deleted_tag = db.find_one_and_delete({"name": name})
        
        if deleted_tag is None:
            msg = f"'?tag {name}' doesn't exist"
            await self.bot.say(block(msg))
        else:    
            msg = f"'?tag {deleted_tag['name']} has been deleted"
            await self.bot.say(block(msg))

    @tag.command(pass_context=True, name="all")
    async def _all(self, ctx):
        """ List all server tags  """
        items = []
        guild = ctx.message.server.id

        with ConnectDatabase(guild) as db:
            tagsList = db.find()  
     
        if tagsList == []:
            await self.bot.say("This server has no tags registered")
        else:
            em = discord.Embed(colour=discord.Colour.default(),
                               title="Server Tags", description="")
            for index, tag in enumerate(tagsList, start=1):
                em.description += f"\n{index}. {tag['name']}"
            await self.bot.send_message(ctx.message.channel, embed=em)

def setup(bot):
    bot.add_cog(Tags(bot))
