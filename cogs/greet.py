from discord.ext import commands


class GreetCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        if ctx.author.bot:
            return
        await ctx.send("hello:)")

    @commands.command()
    async def ping(self, ctx):
        if ctx.author.bot:
            return
        await ctx.send("pong")


def setup(bot):
    bot.add_cog(GreetCog(bot))
