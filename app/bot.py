import time
import random
import asyncio
import discord
import settings
from config import logger
from discord.ext import commands


description = "A discord bot created by a Coconut"

initial_extentions = ('commands.admin', 'commands.concert', 'commands.tags',
                      'commands.sounds')

bot = commands.Bot(command_prefix='?', description=description, pm_help=True,
                       help_attr=dict(hidden=True), formatter=commands.HelpFormatter())

for extension in initial_extentions:
    try:
        bot.load_extension(extension)
        logger.info(f'{extension} extension has been loaded')
    except Exception as e:
        logger.warn(f"Failed to load extention {extension}\n{type(e).__name__}: {e}")

@bot.event
async def on_ready():
    """Logs bot credentials for successful login"""
    users = str(len(set(bot.get_all_members())))
    servers = str(len(bot.guilds))
    channels = str(len(set(bot.get_all_channels())))

    logger.info('EvilRick is logged on')
    logger.info(f"{bot.user} : {bot.user.id}")
    logger.info("-------------")
    logger.info("Connected to:")
    logger.info(f"Users: {users}")
    logger.info(f"Servers: {servers}")
    logger.info(f"Channels: {channels}")

@bot.event
async def on_command_error(ctx, error):
    logger.error(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)

    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    
async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = await bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            await ctx.send(page)
    else:
        pages = await bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            await ctx.send(page)

@bot.command()
@commands.cooldown(1, 20.0, type=commands.BucketType.guild)
async def roll(ctx):
     """Roll the dice"""
     value = random.randrange(0, 101)
     user = ctx.author.display_name
     await ctx.send(f"{user}: **{value}**")


if __name__ == "__main__":
    bot.run(settings.TOKEN)
