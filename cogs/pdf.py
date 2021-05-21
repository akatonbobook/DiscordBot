import datetime
import io
import os

import discord
import pdf2image
import requests
from discord.ext import commands


class PdfCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.poppler_path = os.path.join(self.bot.path, "poppler-0.68.0", "bin")
        os.environ["PATH"] += os.pathsep + self.poppler_path

    @commands.Cog.listener()
    async def on_message(self, message):

        # 実行者がbotなら終了
        if message.author.bot:
            return

        attach = message.attachments
        if len(attach) == 1:
            if '.pdf' == attach[0].filename[-4:]:

                # PDFファイルをダウンロード
                r = requests.get(attach[0].url, stream=True)
                if r.status_code == 200:
                    
                    pdfimages = pdf2image.convert_from_bytes(r.content, fmt="jpg") # 画像ファイルに変換

                    pages = len(pdfimages)  # ページ数
                    askembed = discord.Embed(title="pdf to jpg")
                    askembed.add_field(name="このpdfを変換しますか?", value=attach[0].filename + " " + str(pages) + "ページ分")
                    msg = await message.channel.send(embed=askembed)

                    await msg.add_reaction('🙋‍♂️')

                    limit = datetime.datetime.now() + datetime.timedelta(seconds=300)

                    def check(reaction, user):
                        """リアクションチェック用関数
                        """
                        return user != message.author.bot and str(reaction.emoji) == '🙋‍♂️'

                    while datetime.datetime.now() < limit:
                        try:
                            reaction, user = await self.bot.wait_for("reaction_add", timeout=5, check=check)
                        except: # time out
                            continue # 次のループへ
                        else:
                            if(user.bot):
                                continue

                            # リアクションしたユーザーのDMに画像ファイルを送信
                            dm = await user.create_dm()
                            for idx, image in enumerate(pdfimages):
                                imgbytearr = io.BytesIO()
                                image.save(imgbytearr, format=image.format)
                                imgbytearr = imgbytearr.getvalue()
                                await dm.send(file=discord.File(io.BytesIO(imgbytearr), filename="pdf-image-" + str(idx) + ".jpg"))

                    try:
                        await msg.delete()
                    except Exception:
                        pass


def setup(bot):
    bot.add_cog(PdfCog(bot))