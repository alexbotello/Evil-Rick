from discord.ext import commands
from commands.utils import checks
from config import logger
import time
import youtube_dl
import discord
import pymongo
import settings
import os

OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 
             'libopus.so.0', 'libopus.0.dylib', 'opus']

for opus_lib in OPUS_LIBS:
    try:
        discord.opus.load_opus(opus_lib)
    except OSError:
        pass
        
logger.info(f"Opus Library Loaded: {discord.opus.is_loaded()}")


class VoiceConnection:
    def __init__(self, bot):
        self.bot = bot
        self.voice = None


class Sounds:
    """ Sound related commands for Evil Rick """

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
    
    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceConnection(self.bot)
            self.voice_states[server.id] = state
        return state
    
    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice


    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    @checks.is_owner()
    async def join(self, ctx, *, channel : discord.Channel):
        """Enables Bot Sounds """
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel...')
        else:
            await self.bot.say('Sounds are enabled in ' + channel.name)
    

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            
        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

       


    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def stfu(self, ctx):
        """SHUT THE FUCK UP!""" 
        
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=wQYob6dpTTk')
        player.start()
        
        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def pump(self, ctx):
        """I'm here to pump you up"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://youtu.be/BgWd1dcODHU?t=10')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")


    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def listen(self, ctx):
        """Listen here you beautiful bitch...."""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=Jsi5VTzJpPw')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")


    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def plums(self, ctx):
        """...a nice bluish hue"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=7cIAcXpUuS0')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")

    
    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def hadtosay(self, ctx):
        """Shiiiiit, Negro! That's all you had to say"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=hRb7-3kebUQ')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def omg(self, ctx):
        """Oh my god, who the hell cares?"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=RFZrzg62Zj0')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def damn(self, ctx):
        """DAAAAAMMMMMMMMMNNNNN!"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=w1EHH0_CqqU')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def dominate(self, ctx):
        """Dominating"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=tq65HEqNq-8')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

def setup(bot):
    bot.add_cog(Sounds(bot))
