from discord.ext import commands
from config import logger
from commands.utils import checks
from commands.utils.formatter import block
import pymongo
import discord
import settings


class Tags:
    """ Tag related commands for Cocobot """

    def __init__(self, bot):
        self.bot = bot
        self.client = pymongo.MongoClient(settings.DB_URL)
    

    def connect_database(self, name):
        db = self.client.settings.DB_NAME
        collection = db[str(name)]
        return collection


    @commands.group(invoke_without_command=True, pass_context=True)
    async def tag(self, ctx, *, name):
        """ Retrieve a tag command from the server """

        guild = ctx.message.server
        tags = self.connect_database(guild)

        try:
            tag = tags.find_one({"name": name})

            if tag is None:
                raise TypeError

            content = tag['content']
            await self.bot.say(content)

        except TypeError:
            await self.bot.say('No tag was found...')

        finally:
            self.client.close()


    @tag.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def create(self, ctx, name, *, content):
        """ Create a new tag for the server """

        guild = ctx.message.server
        tags = self.connect_database(guild)

        try:
            tag = tags.find_one({"name": name})

            if tag:
                raise pymongo.errors.InvalidName

            tag = { "name": name,
                    "content": content,
                    "creator": str(ctx.message.author)
                  }

            tags.insert_one(tag)
            msg = f"'?tag {tag['name']}' has been created by {tag['creator']}"
            await self.bot.delete_message(ctx.message)
            await self.bot.say(block(msg))

        except pymongo.errors.InvalidName:
            await self.bot.say("Tag already exists...")

        finally:
            self.client.close()


    @tag.command(pass_context=True)
    @commands.has_permissions(administrator=True, ban_members=True)
    @checks.is_owner()
    async def remove(self, ctx, *, name):
        """ Remove specified tag from server """

        guild = ctx.message.server
        tags = self.connect_database(guild)

        try:
            deleted_tag = tags.find_one_and_delete({"name": name})

            if deleted_tag is None:
                raise TypeError

            msg = f"'?tag {deleted_tag['name']} has been deleted"
            await self.bot.say(block(msg))

        except TypeError:
            msg = f"'?tag {name}' doesn't exist"
            await self.bot.say(block(msg))

        finally:
            self.client.close()


    @tag.command(pass_context=True, name="all")
    async def _all(self, ctx):
        """ List all server tags  """

        items = []
        guild = ctx.message.server
        tags = self.connect_database(guild)

        try:
            tagsList = tags.find()

            if tagsList == []:
                raise ValueError

            for index, tag in enumerate(tagsList, start=1):
                items.append(f"{index}.\t{tag['name']}\n")

            em = discord.Embed(colour=discord.Colour.default(),
                               title="Server Tags", description="")

            em.description = "".join(items)
            await self.bot.send_message(ctx.message.channel, embed=em)

        except ValueError:
            await self.bot.say("This server has no tags registered")

        finally:
            self.client.close()


def setup(bot):
    bot.add_cog(Tags(bot))
