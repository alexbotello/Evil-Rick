from discord.ext import commands
from config import logger
import time
import random
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
    

    async def on_voice_state_update(self, before, after):
        """ Greets a user who joins the voice channel"""
        greetings = ['https://www.youtube.com/watch?v=evtmNulZAj0',
                     'https://www.youtube.com/watch?v=9SL35HaJ2Ys']

        before_members = []
        after_members = []
     
        if before.is_afk or after.is_afk:
            pass
        elif before.deaf or after.deaf:
            pass
        elif before.self_mute or after.self_mute:
            pass
        elif before.mute or after.mute:
            pass
        elif before.self_deaf or after.self_deaf:
            pass

        if before.voice_channel:
            channel = before.voice_channel
            users = channel.voice_members
            for u in users:
                before_members.append(u.name)

        if after.voice_channel:
            channel = after.voice_channel
            users = channel.voice_members
            for u in users:
                after_members.append(u.name)
     
            if len(before_members) < len(after_members):
                state = self.get_voice_state(after.server)
                player = await state.voice.create_ytdl_player(random.choice(greetings))
                player.start()

       
    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def join(self, ctx, *, channel : discord.Channel):
        """Specify a channel for the bot to join """
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel...')
      
    

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
    @commands.has_permissions(create_instant_invite=True)
    async def stfu(self, ctx): 
        """SHUT THE FUCK UP!""" 
        
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=wQYob6dpTTk')
        player.start()
        
        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def pump(self, ctx):
        """I'm here to pump you up"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://youtu.be/BgWd1dcODHU?t=10')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")


    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def listen(self, ctx):
        """Listen here you beautiful bitch...."""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=Jsi5VTzJpPw')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")


    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def plums(self, ctx):
        """...a nice bluish hue"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=7cIAcXpUuS0')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")

    
    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def hadtosay(self, ctx):
        """Shiiiiit, Negro! That's all you had to say"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=hRb7-3kebUQ')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def omg(self, ctx):
        """Oh my god, who the hell cares?"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=RFZrzg62Zj0')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def damn(self, ctx):
        """DAAAAAMMMMMMMMMNNNNN!"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=w1EHH0_CqqU')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def dominate(self, ctx):
        """Dominating"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=tq65HEqNq-8')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def wub(self, ctx):
        """Wubba Lubba Dub Dub"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=PAhoNoQ91_c')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")
    

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    async def pickle(self, ctx):
        """I'm Pickle Rick!"""
        state = self.get_voice_state(ctx.message.server)
        player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=Ij7ayjBaNhc')
        player.start()

        if player.error:
            logger.error(f"Error: {player.error} occured while streaming audio")


def setup(bot):
    bot.add_cog(Sounds(bot))
