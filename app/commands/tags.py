from discord.ext import commands
from utils.formatter import block
from utils.paginator import Pages
from config import logger, TagDatabase


class Tags:
    """ 
    Tag Command Cog
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, *, name):
        """
        Retrieve a tag from the database
        """
        guild = ctx.guild.id
        with TagDatabase(guild) as db:
            tag = db.get_tag(name)
            await ctx.send(tag['content'])
    
    @tag.command()
    @commands.has_permissions(create_instant_invite=True)
    async def create(self, ctx, name, *, content):
        """ 
        Create a tag for the server 
        """
        guild = ctx.guild.id
        with TagDatabase(guild) as db:
            tag = { "name": name,
                    "content": content,
                    "creator": ctx.author.display_name
                }
            db.create_tag(tag)
            msg = f"?tag {name} has been created by {tag['creator']}"
            await ctx.message.delete()
            await ctx.send(block(msg))
            
    @tag.command()
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx, *, name):
        """
        Remove a tag from server
        """
        guild = ctx.guild.id
        with TagDatabase(guild) as db:
            db.delete_tag(name)
            msg = f"'?tag {name}' has been removed"
            await ctx.send(msg)
    
    @tag.command(name="all")
    async def _all(self, ctx):
        """
        List all server tags
        """
        guild = ctx.guild.id
        with TagDatabase(guild) as db:
            tags = db.get_all_tags()
            tags = sorted([tag["name"] for tag in tags])

            p = Pages(ctx, entries=tags, per_page=20)
            await p.paginate() 

def setup(bot):
    bot.add_cog(Tags(bot))
