import discord
from discord.ext import commands

import settings
import errors
from config import logger


description = "A discord bot created by a Coconut"

initial_extentions = ('commands.admin', 'commands.concert', 'commands.tags',
                      'commands.sounds', 'commands.misc')

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
    """
    Logs bot credentials on successful startup
    """
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
    error = getattr(error, 'original', error)

    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)

    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)

    elif isinstance(error, errors.DuplicateArtist):
        await ctx.send("Artist has already been saved")

    elif isinstance(error, errors.MissingArtist):
        await ctx.send("Cannot remove an artist that has not been saved")

    elif isinstance(error, errors.NotFound):
        await ctx.send("Nothing was found...")

    elif isinstance(error, errors.TagAlreadyExists):
        await ctx.send("Tag already exists...")

    elif isinstance(error, errors.SoundAlreadyExists):
        await ctx.send("A sound with that name already exists...")

    elif isinstance(error, discord.ClientException):
        await ctx.send("Command failed. Already connected/playing")

    elif isinstance(error, discord.Forbidden):
        await ctx.send("You do not have permission to use this command")

    elif isinstance(error, AttributeError):
        await ctx.send("Not in a voice channel...")

    elif isinstance(error, discord.HTTPException):
        await ctx.send("You can only bulk delete messages that "
                       "are under 14 days old")


async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = await bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            await ctx.send(page)
    else:
        pages = await bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            await ctx.send(page)

if __name__ == "__main__":
    bot.run(settings.TOKEN)
