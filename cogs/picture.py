import datetime
import os

import discord
import requests
from discord.ext import commands


class Picture(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.path = os.path.join(os.path.dirname(__file__))

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        attach = message.attachments
        if len(attach) == 1:
            if attach[0].filename[-4:] == '.jpg' or attach[0].filename[-4:] == '.png':
                ext = attach[0].filename[-4:]
                r = requests.get(attach[0].url, stream=True)
                if r.status_code == 200:
                    
                    try:
                        os.mkdir(self.bot.path + '\\pictures\\')
                    except:
                        pass
                    channelname = message.guild.name + '-' + message.channel.name if type(message.channel) != discord.DMChannel else "DMChannel"
                    fname = datetime.datetime.now().strftime(self.bot.path + '\\pictures\\' + channelname + '-' + message.author.name + '-%Y%m%d%H%M%S' + ext)
                    with open(fname, 'wb') as f:
                        f.write(r.content)              


def setup(bot):
    bot.add_cog(Picture(bot))