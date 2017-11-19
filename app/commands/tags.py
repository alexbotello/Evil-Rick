import pymongo
import discord
import settings
from discord.ext import commands
from commands.utils.formatter import block
from config import logger, ConnectDatabase


class Tags:
    """ Tag Command Cog """

    def __init__(self, bot):
        self.bot = bot
        #self.paginator = commands.Paginator(max_size=99)

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, *, name):
        """
        Retrieve a tag from the server database
        """       
        with ConnectDatabase(ctx.guild.id) as db:
            tags = db
            tag = tags.find_one({"name": name}) 
    
        if tag is None:
            await ctx.send('No tag was found...')
        else:
            content = tag['content']
            await ctx.send(content)
        
    @tag.command()
    @commands.has_permissions(create_instant_invite=True)
    async def create(self, ctx, name, *, content):
        """ 
        Create a tag for the server 
        """
        with ConnectDatabase(ctx.guild.id) as db:
            tag = db.find_one({"name": name})
            if tag:
                await ctx.send("Tag already exists...")
            else:
                tag = { "name": name,
                        "content": content,
                        "creator": ctx.author.display_name
                }
                db.insert_one(tag)

                msg = f"'?tag {tag['name']}' has been created by {tag['creator']}"
                await ctx.message.delete()
                await ctx.send(block(msg))
            
    @tag.command()
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx, *, name):
        """ 
        Remove a tag from server
        """
        with ConnectDatabase(ctx.guild.id) as db:
            deleted_tag = db.find_one_and_delete({"name": name})
        
        if deleted_tag is None:
            msg = f"'?tag {name}' doesn't exist"
            await ctx.send(block(msg))
        else:    
            msg = f"'?tag {deleted_tag['name']} has been deleted"
            await ctx.send(block(msg))

    @tag.command(name="all")
    async def _all(self, ctx):
        """ 
        List all server tags
        """
        items = []
        with ConnectDatabase(ctx.guild.id) as db:
            tagsList = db.find()  
     
        if tagsList == []:
            await ctx.send("This server has no tags registered")
        else:
            em = discord.Embed(colour=discord.Colour.default(),
                               title="Server Tags", description="")
            for index, tag in enumerate(tagsList, start=1):
                em.description += f"\n{index}. {tag['name']}"
            await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Tags(bot))
