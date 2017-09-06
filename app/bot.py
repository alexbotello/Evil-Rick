import time
import asyncio
import discord
import settings
from config import logger
from discord.ext import commands


description = "A discord bot created by a Coconut"
formatter = commands.HelpFormatter(show_check_failure=False)

initial_extentions = ('commands.admin', 'commands.concert', 'commands.tags',
                      'commands.sounds')

bot = commands.Bot(command_prefix='?', description=description, pm_help=True,
                       help_attr=dict(hidden=True), formatter=formatter)

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
    servers = str(len(bot.servers))
    channels = str(len(set(bot.get_all_channels())))

    logger.info('EvilRick is logged on')
    logger.info(f"{bot.user} : {bot.user.id}")
    logger.info("-------------")
    logger.info("Connected to:")
    logger.info(f"Users: {users}")
    logger.info(f"Servers: {servers}")
    logger.info(f"Channels: {channels}")


@bot.event
async def on_command_error(error, ctx):
    logger.error(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)

    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)


@bot.command(pass_context=True)
async def test(ctx):
     """This is a test command"""
     await bot.say('This is a test message')


if __name__ == "__main__":
    bot.run(settings.TOKEN)
