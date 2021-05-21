import io

import discord
import requests
from discord.ext import commands

cat_url = 'https://aws.random.cat/meow'
dog_url = 'https://dog.ceo/api/breeds/image/random'
fox_url = 'https://randomfox.ca/floof/'


class AnimalCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cat(self, ctx):
        if ctx.author.bot:
            return
        else:
            r = requests.get(cat_url)
            ext = r.json()["file"].split(".")[-1]
            r = requests.get(r.json()["file"])
            if r.status_code == 200:
                await ctx.channel.send(file=discord.File(io.BytesIO(r.content), "cat." + ext))

    @commands.command()
    async def dog(self, ctx):
        if ctx.author.bot:
            return
        else:
            r = requests.get(dog_url)
            ext = r.json()["message"].split(".")[-1]
            r = requests.get(r.json()["message"])
            if r.status_code == 200:
                await ctx.channel.send(file=discord.File(io.BytesIO(r.content), "dog." + ext))

    @commands.command()
    async def fox(self, ctx):
        if ctx.author.bot:
            return
        else:
            r = requests.get(fox_url)
            ext = r.json()["image"].split(".")[-1]
            r = requests.get(r.json()["image"])
            if r.status_code == 200:
                await ctx.channel.send(file=discord.File(io.BytesIO(r.content), "fox." + ext))


def setup(bot):
    bot.add_cog(AnimalCog(bot))