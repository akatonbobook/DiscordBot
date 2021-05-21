import io

import discord
from discord.ext import commands
import requests

# RestAPIのエントリポイント
url = 'https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={d}'

class QrCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def qr(self, ctx, data):

        # 送信者がボットなら終了
        if ctx.author.bot:  
            return

        # RestAPIを叩く
        r = requests.get(url.format(d=data))

        # チャンネルに画像を送信
        if r.status_code == 200:
            await ctx.channel.send(file=discord.File(io.BytesIO(r.content), 'qr.png'))


def setup(bot):
    bot.add_cog(QrCog(bot))
    