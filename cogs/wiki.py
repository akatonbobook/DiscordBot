import requests
from discord.ext import commands


url1 = 'https://{language}.wikipedia.org/w/api.php'


class WikiCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wiki(self, ctx, word, n = 1, lg = 'ja'):
        if ctx.author.bot:
            return
        url = url1.format(url1, language = lg)
        paydata = {'action':'query', 'list':'search', 'srsearch':word, 'format':'json'}
        r = requests.get(url, params=paydata)
        msg = 'これのこと？\n'
        msg += ('https://' + lg + '.wikipedia.org/wiki/' + r.json()['query']['search'][n - 1]['title'])
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(WikiCog(bot))