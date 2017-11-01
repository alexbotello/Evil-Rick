import random
import shutil
import asyncio
import discord
import pymongo
import youtube_dl
import settings
from config import logger
from discord.ext import commands

OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll',
             'libopus.so.0', 'libopus.0.dylib', 'opus']

for opus_lib in OPUS_LIBS:
    try:
        discord.opus.load_opus(opus_lib)
    except OSError:
        pass

logger.info(f"Opus Library Loaded: {discord.opus.is_loaded()}")

ytdl_format_options = {"format": "bestaudio/best", "extractaudio": True, "audioformat": "mp3", 
                       "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": False, 
                       "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto", 
                       "source_address": "0.0.0.0", "preferredcodec": "libmp3lame"}

def get_ytdl(id):
    format = ytdl_format_options
    format['outtmpl'] = "commands/sounds/{}/%(id)s.mp3".format(id)
    return youtube_dl.YoutubeDL(format)

class VoiceConnection:
    def __init__(self, bot, guild):
        self.bot = bot
        self.voice = None
        self.guild = guild
        self.conn = self.bot.loop.create_task(self._clear_data())
    
    async def _clear_data(id=None):
        await self.bot.wait_until_ready()
        counter = 0
        while not self.bot.is_closed():
            counter += 1
            logger.info(f"CLEARED YOUTUBE DATA: {counter}")
            if id is None:
                shutil.rmtree('commands/sounds')
            else:
                shutil.rmtree(f"commands/sounds/{id}")
            await asyncio.sleep(60 * 180) # 3 hours

class Sounds:
    """ Sound related commands for Evil Rick """
    rate = 1
    per = 4.0

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
        self.greetings = ['https://www.youtube.com/watch?v=evtmNulZAj0',
                          'https://www.youtube.com/watch?v=9SL35HaJ2Ys',
                          'https://www.youtube.com/watch?v=XuI5sV_-kx0',
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
        """ Greets a user who joins the voice channel"""
        tim = 142914172089401344
        state = self.get_voice_state(member.guild)
        if state.voice.channel == member.voice.channel:
            if (after.deaf or after.self_deaf) or (before.deaf or before.self_deaf):
                pass
            elif (after.mute or after.self_mute) or (before.mute or before.self_mute):
                pass
            elif after.afk or before.afk:
                pass
            else: 
                try:
                    if member.id == tim:
                        url = 'https://www.youtube.com/watch?v=EDrMco4g8ng'
                        audio = self.download_video(member.guild.id, url)
                        state.voice.play(audio)
                    else:
                        url = random.choice(self.greetings)
                        audio = self.download_video(member.guild.id, url)
                        state.voice.play(audio)
                
                except youtube_dl.utils.DownloadError as error:
                    logger.error(f"{error}: failed to download link")
                    member.send("Failed to download link from youtube...")

                except discord.ClientException:
                    logger.error('An error occured while streaming audio...')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def join(self, ctx, *, channel : commands.VoiceChannelConverter):
        """Specify a channel for the bot to join """
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await ctx.send('Already in a voice channel...')
        except discord.InvalidArgument:
            await ctx.send('This is not a voice channel...')

    @commands.command(no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        channel = ctx.author.voice.channel
        if channel is None:
            await ctx.send('You are not in a voice channel.')

        state = self.get_voice_state(ctx.guild)
        if state.voice is None:
            state.voice = await channel.connect(reconnect=True)
        else:
            await state.voice.move_to(channel)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def clear(self, ctx):
        """ Clear downloaded youtube files """
        state = self.get_voice_state(ctx.guild)
        try:
            state.clear_data(ctx.guild.id)
        except FileNotFoundError:
            await ctx.author.send("No audio files to be cleared...")

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def stfu(self, ctx):
        """SHUT THE FUCK UP!"""
        url = 'https://www.youtube.com/watch?v=wQYob6dpTTk'
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")
        
        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def pump(self, ctx):
        """I'm here to pump you up"""
        url = 'https://youtu.be/BgWd1dcODHU?t=10'
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")
        
        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def listen(self, ctx):
        """Listen here you beautiful bitch...."""
        url = 'https://www.youtube.com/watch?v=Jsi5VTzJpPw'
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")
        
        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def plums(self, ctx):
        """...a nice bluish hue"""
        url = 'https://www.youtube.com/watch?v=7cIAcXpUuS0'
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def hadtosay(self, ctx):
        """Shiiiiit, Negro! That's all you had to say"""
        url = "https://www.youtube.com/watch?v=hRb7-3kebUQ"
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def omg(self, ctx):
        """Oh my god, who the hell cares?"""
        url = 'https://www.youtube.com/watch?v=RFZrzg62Zj0'
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)

        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def damn(self, ctx):
        """DAAAAAMMMMMMMMMNNNNN!"""
        url = "https://www.youtube.com/watch?v=w1EHH0_CqqU"
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def dominate(self, ctx):
        """Dominating"""
        url = 'https://www.youtube.com/watch?v=tq65HEqNq-8'
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)

        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def wub(self, ctx):
        """Wubba Lubba Dub Dub"""
        url = 'https://www.youtube.com/watch?v=PAhoNoQ91_c'
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def pickle(self, ctx):
        """I'm Pickle Rick!"""
        url = 'https://www.youtube.com/watch?v=Ij7ayjBaNhc'
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)

        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def gold(self, ctx):
        """I Love Gold"""
        url = 'https://www.youtube.com/watch?v=DOFAnpb8I3E'
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)

        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")   
        
        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def bitch(self, ctx):
        """Like A Bitch"""
        url = 'https://www.youtube.com/watch?v=koCAtBJA5XU'
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")  

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def leeroy(self, ctx):
        """....jenkins!"""
        url = "https://www.youtube.com/watch?v=yOMj7WttkOA"
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")  

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def ree(self, ctx):
        """REEEEEEEEE!"""
        url = "https://www.youtube.com/watch?v=cLBq9vrWGuE"
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")  

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def horny(self, ctx):
        """DO I MAKE YOU RANDY!?!"""
        url = "https://www.youtube.com/watch?v=gXlIymq7ofE"
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(url)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...")  

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        
    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.guild)
    async def triple(self, ctx):
        """Oh baby a triple, oh yeah!"""
        url = "https://www.youtube.com/watch?v=13VFfsJTLdc"
        state = self.get_voice_state(ctx.guild)
        try:
            audio = self.download_video(ctx.guild.id, url)
            state.voice.play(audio)
        
        except youtube_dl.utils.DownloadError as error:
            logger.error(f"{error}: failed to download link")
            ctx.send("Failed to download link from youtube...") 

        except discord.ClientException:
            ctx.send('An error occured while streaming audio...')
        

def setup(bot):
    bot.add_cog(Sounds(bot))