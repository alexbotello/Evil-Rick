import random
import shutil
import asyncio
import discord
import pymongo
import youtube_dl
import settings
from config import logger
from discord.ext import commands

ytdl_format_options = {"format": "bestaudio/best", "extractaudio": True, "audioformat": "mp3", 
                       "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": False, 
                       "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto", 
                       "source_address": "0.0.0.0", "preferredcodec": "libmp3lame"}

def get_ytdl(id):
    format = ytdl_format_options
    format['outtmpl'] = "commands/sounds/{}/%(id)s.mp3".format(id)
    return youtube_dl.YoutubeDL(format)


class OpusLoader:
    def __init__(self):
        self.opus_libs = [ 'libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll',
                            'libopus.so.0', 'libopus.0.dylib', 'opus' ]
        self.load_opus()
        logger.info(f"Opus Library Loaded: {discord.opus.is_loaded()}")

    def load_opus(self):
        for opus_lib in self.opus_libs:
            try:
                discord.opus.load_opus(opus_lib)
            except OSError:
                pass

class VoiceConnection:
    """
    Represents a discord voice client
    """
    def __init__(self, bot, guild):
        self.bot = bot
        self.voice = None
        self.guild = guild
        self.bot.loop.create_task(self.clear_data())
  
    async def clear_data(self, id=None):
        await self.bot.wait_until_ready()
        counter = 0
        while not self.bot.is_closed():
            try:
                if id is None:
                    shutil.rmtree('commands/sounds')
                else:
                    shutil.rmtree(f"commands/sounds/{id}")
                counter += 1
                logger.info(f"CLEARED YOUTUBE DATA: {counter}")
            except FileNotFoundError:
                logger.info(f"No Youtube Data Detected")
            await asyncio.sleep(60*60) # 1 Hour

class Sounds:
    """ 
    Sound Command Cog
    """
    # Cooldown parameters
    rate = 1
    per = 4.0

    def __init__(self, bot):
        opus = OpusLoader()
        self.bot = bot
        self.voice_states = {}
        self.greetings = ['https://www.youtube.com/watch?v=evtmNulZAj0',
                          'https://www.youtube.com/watch?v=9SL35HaJ2Ys',
                          'https://youtu.be/B7lgrFKI_L8']
    @staticmethod
    def download_video(id, url):
        ytdl = get_ytdl(id)
        data =  ytdl.extract_info(url, download=True)
        
        if "entries" in data:
            data = data['entries'][0]
        
        title = data['title']
        _id = data['id']
        duration = None

        try:
            duration = data['duration']
        except KeyError:
            pass
        
        path = f"commands/sounds/{id}"
        fp = f"{path}/{_id}.mp3"
        audio = discord.FFmpegPCMAudio(fp, executable="avconv")
        
        return audio

    def get_voice_state(self, guild):
        state = self.voice_states.get(guild.id)
        if state is None:
            state = VoiceConnection(self.bot, guild)
            self.voice_states[guild.id] = state
        return state

    async def create_voice_client(self, channel):
        voice = await channel.connect(reconnect=True)
        state = self.get_voice_state(channel.guild)
        state.voice = voice
    
    async def on_voice_state_update(self, member, before, after):
        """
        Automatically greets a user who joins the voice channel
        """
        timmy = {142914172089401344: 'https://www.youtube.com/watch?v=EDrMco4g8ng'}
        state = self.get_voice_state(member.guild)
        try:
            if before.channel != state.voice.channel:
                if member.id in timmy:
                    audio = self.download_video(member.guild.id, tim[member.id])
                    state.voice.play(audio)
                else:
                    url = random.choice(self.greetings)
                    audio = self.download_video(member.guild.id, url)
                    state.voice.play(audio)                    
        except AttributeError:
            logger.info("Skipping Initial Voice Check")
    
    def play_sound(self, ctx, url):
        state = self.get_voice_state(ctx.guild)
        audio = self.download_video(ctx.guild.id, url)
        state.voice.play(audio)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def join(self, ctx, *, channel : commands.VoiceChannelConverter):
        """
        Specify a channel for the bot to join
        """
        await self.create_voice_client(channel)

    @commands.command(no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def summon(self, ctx):
        """
        Summons the bot to your voice channel
        """
        channel = ctx.author.voice.channel
        if channel is None:
            await ctx.send('You are not in a voice channel.')

        state = self.get_voice_state(ctx.guild)
        if state.voice is None:
            state.voice = await channel.connect(reconnect=True)
        else:
            await state.voice.move_to(channel)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def stfu(self, ctx):
        """
        stfu
        """
        url = 'https://www.youtube.com/watch?v=wQYob6dpTTk'
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def pump(self, ctx):
        """
        Get pumped up
        """
        url = 'https://youtu.be/BgWd1dcODHU?t=10'
        self.play_sound(ctx, url)


    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def listen(self, ctx):
        """
        Listen here you beautiful bitch....
        """
        url = 'https://www.youtube.com/watch?v=Jsi5VTzJpPw'
        self.play_sound(ctx, url)

        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def plums(self, ctx):
        """
        ...a nice bluish hue
        """
        url = 'https://www.youtube.com/watch?v=7cIAcXpUuS0'
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def hadtosay(self, ctx):
        """
        Shiiiiit, Negro! That's all you had to say
        """
        url = "https://www.youtube.com/watch?v=hRb7-3kebUQ"
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def omg(self, ctx):
        """
        Oh my god, who the hell cares?
        """
        url = 'https://www.youtube.com/watch?v=RFZrzg62Zj0'
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def damn(self, ctx):
        """
        Daaaaaammmmmmmnnnnnn!
        """
        url = "https://www.youtube.com/watch?v=w1EHH0_CqqU"
        self.play_sound(ctx, url)
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def dominate(self, ctx):
        """
        Dominating!
        """
        url = 'https://www.youtube.com/watch?v=tq65HEqNq-8'
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def wub(self, ctx):
        """
        Wubba Lubba Dub Dub
        """
        url = 'https://www.youtube.com/watch?v=PAhoNoQ91_c'
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def pickle(self, ctx):
        """
        I'm pickle rick!
        """
        url = 'https://www.youtube.com/watch?v=Ij7ayjBaNhc'
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def gold(self, ctx):
        """
        I love gold
        """
        url = 'https://www.youtube.com/watch?v=DOFAnpb8I3E'
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def bitch(self, ctx):
        """
        Does he look like a bitch?
        """
        url = 'https://www.youtube.com/watch?v=koCAtBJA5XU'
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def leeroy(self, ctx):
        """
        ....jenkins!
        """
        url = "https://www.youtube.com/watch?v=yOMj7WttkOA"
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def ree(self, ctx):
        """
        REEEEEEEEE!
        """
        url = "https://www.youtube.com/watch?v=cLBq9vrWGuE"
        self.play_sound(ctx, url)

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def horny(self, ctx):
        """
        Do I make you horny, baby?
        """
        url = "https://www.youtube.com/watch?v=gXlIymq7ofE"
        self.play_sound(ctx, url)
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def triple(self, ctx):
        """
        Oh baby a triple, oh yeah!
        """
        url = "https://www.youtube.com/watch?v=13VFfsJTLdc"
        self.play_sound(ctx, url)

def setup(bot):
    bot.add_cog(Sounds(bot))