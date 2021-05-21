import discord
from discord.ext import commands

from audio import audiosource


class NoVoiceClientError(Exception):
    """ギルドにボイスクライアントが存在しないことを知らせる例外
    """
    pass


class VoiceChannelNotFoundError(Exception):
    """ボイスチャンネルが見つからないことを知らせる例外
    """
    pass


class VoiceCore(commands.Cog):
    """オーディオ関係の基本クラス
    """

    def __init__(self, bot):
        self.bot = bot

    async def pause_source(self, channel: discord.VoiceChannel):
        """オーディオを一時停止する関数

        :param channel:
        """
        voice_client = self.get_voice_client(channel.guild)
        if voice_client == None:
            return
        if voice_client.channel == channel:
            voice_client.pause()

    def stop_source(self, guild: discord.Guild):
        """オーディオを止める関数

        :param guild: ギルド
        """
        voice_client = self.get_voice_client(guild)
        if voice_client == None:
            return
        if voice_client.is_playing():
            voice_client.stop()

    async def play_source(self, channel: discord.VoiceChannel, original_source: discord.AudioSource,
                          *, after=None, enter=True, volume=0.05):
        """AudioSourceを再生する関数

        :param channel: 再生するボイスチャンネル
        :param original_source: 再生するAudioSource
        :param after:　再生終了後のアクション
        :param enter:　入室するかどうか
        :param volume:　音量
        """
        # enter==Trueなら入室
        if enter:
            await self.enter_voice_channel(channel)

        voice_client = self.get_voice_client(channel.guild)
        if voice_client is None:
            return
        else:
            source = audiosource.MyPCMVolumeTransformer(original_source, volume)
            if voice_client.is_playing():
                voice_client.stop()
            voice_client.play(source, after=after)

    def get_original_audio_source(self, guild: discord.Guild):
        """ギルドに対応するVoiceClientのAudioSourceから元のAudioSourceを返す

        :param guild:　ギルド
        :except NoVoiceClientError: ギルドに対応するVoiceClientが存在しない場合に発生
        :return: ギルドのVoiceClientが持つAudioSource
        """
        try:
            voice_client = self.get_voice_client(guild)
            if voice_client == None:
                raise NoVoiceClientError
            return voice_client.source.original
        except Exception as e:
            raise e

    async def leave_voice_channel(self, channel: discord.VoiceChannel):
        """ボイスチャンネルから退出する関数

        指定したボイスチャンネルから退出する.
        指定したボイスチャンネルにボットが入室していない場合，何もしない.

        :param channel: ボイスチャンネル
        :return bool: 退出した場合True，ボイスチャンネルにボットが入室していなかった場合False
        """
        voice_client = self.get_voice_client(channel.guild)
        
        if voice_client.channel == channel:
            await voice_client.disconnect()

            try:
                self.bot.voice_clients.remove(voice_client)
            except:
                pass

            return True
        return False

    async def enter_voice_channel(self, channel: discord.VoiceChannel):
        """ボイスチャンネルに入室する関数

        ギルド内の別チャンネルに入室している場合は移動.
        ボイスチャンネルに入室していない場合は新たに接続

        :param channel: ボイスチャンネル
        """
        voice_client = self.get_voice_client(channel.guild)
        if voice_client == None:
            await channel.connect()
        elif voice_client.channel == channel:
            return
        else:
            await voice_client.move_to(channel)

    def get_voice_client(self, guild: discord.Guild):
        """ギルドに対応するVoiceClientを返す関数

        対応するVoiceClientがなければ None

        :param guild: ギルド
        :return: VoiceClient
        """
        for voice_client in self.bot.voice_clients:
            if voice_client.guild == guild:
                return voice_client
        else:
            return None


class VoiceCog(VoiceCore):

    @commands.command()
    async def join(self, ctx):
        """ボットを入室させる
        """
        if ctx.author.bot:
            return
        if ctx.author.voice == None:
            await ctx.send("ボイスチャンネルから呼んでね")
        await self.enter_voice_channel(ctx.author.voice.channel)

    @commands.command()
    async def bye(self, ctx):
        """ボットを退出させる
        """
        if ctx.author.bot:
            return
        if ctx.author.voice == None:
            await ctx.send("ボイスチャンネルから実行してね")
            return
        self.stop_source(ctx.author.voice.channel.guild)
        result = await self.leave_voice_channel(ctx.author.voice.channel)
        if not result:
            await ctx.send("botは入室していないよ")

    @commands.command()
    async def stop(self, ctx):
        """ボットの音源を止める（stop)
        """
        if ctx.author.bot:
            return
        if ctx.author.voice == None:
            await ctx.send("ボイスチャンネルから実行してね")
        self.stop_source(ctx.author.voice.channel.guild)


def setup(bot):
    bot.add_cog(VoiceCog(bot))
