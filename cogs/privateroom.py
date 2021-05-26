import discord
from discord.ext import commands


class PrivateRoomCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def pc(self, ctx):
        if ctx.author.id != 490866292585136128:
            await ctx.send("このコマンドを実行する権限がありません")
            return
        await self.fetch_all()

    def is_PC_exist(self, vc):
        for tc in g.text_channels:
            if tc.name.lower() == (vc.name + "_pc").lower():
                return True
        else:
            return False
    
    def is_Role_exist(self, vc):
        for role in g.roles:
            if role.name.lower() == (vc.name + '_members').lower():
                return True
        else:
            return False
    
    def get_tc_from_name(self, guild, name):
        for tc in guild.text_channels:
            if tc.name.lower() == name.lower():
                return tc
        else:
            return None
    
    def get_role_from_name(self, guild, name):
        for role in guild.roles:
            if role.name.lower() == name.lower():
                return role
        else:
            return None

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        
        if before.channel == after.channel:
            return
        
        if before.channel:  #退室処理
            #   プライベートチャンネルまたはロールが存在したら
            old_role = self.get_role_from_name(before.channel.guild, before.channel.name+"_members")
            old_pc = self.get_tc_from_name(before.channel.guild, before.channel.name+"_pc")
            if old_role:
                await member.remove_roles(old_role) #   ロールを外す
                if len(before.channel.members) == 0 or (len(before.channel.members) == 1 and before.channel.members[0].bot):   #在室ｰ>0人のとき
                    try:
                        await old_role.delete()     #   ロールを削除
                    except:
                        print("ロール削除に失敗")
                    try:
                        await old_pc.delete()       #   プライベートチャンネルを削除
                    except Exception as e:
                        print(e)
                        print("テキストチャンネル削除に失敗")
        
        if after.channel: #入室処理
            new_role_name = after.channel.name + "_members"
            new_pc_name = after.channel.name + "_pc"
            new_role = self.get_role_from_name(after.channel.guild, new_role_name)
            new_pc = self.get_tc_from_name(after.channel.guild, new_pc_name)
            g = after.channel.guild
            if not new_role or not new_pc:  #   一人目の入室
                try:
                    try:
                        if not new_role:    #   ロールがなかったら
                            new_role = await g.create_role(name=new_role_name)
                    except:
                        print("ロール作成に失敗")
                        return
                    overwrites = {
                        g.default_role: discord.PermissionOverwrite(read_messages=False),
                        g.me: discord.PermissionOverwrite(read_messages=True),
                        new_role: discord.PermissionOverwrite(read_messages=True, manage_channels=False, manage_messages=False)
                    }
                    try:
                        if not new_pc:      #   プライベートチャンネルが存在しなかったら
                            new_pc = await g.create_text_channel(name=new_pc_name, overwrites=overwrites, category=after.channel.category)
                            message = await new_pc.send("全員が退出するとこのテキストチャンネルは削除されます。")
                            await message.pin()
                    except Exception as e:
                        print(e)
                        print("テキストチャンネル作成に失敗")
                        return
                    for m in after.channel.members:
                        if not new_role in m.roles:
                            await m.add_roles(new_role)
                except Exception as e:
                    print(e)
                    print("初期化処理に失敗")
                    return

            await member.add_roles(new_role)


    async def fetch_all(self):
        for g in self.bot.guilds:
            for vc in g.voice_channels:

                async def create_PC(vc):
                    try:
                        role_name = vc.name + "_members"
                        pc_name = vc.name + "_pc"
                        new_role = self.get_role_from_name(g, role_name)
                        new_pc = self.get_tc_from_name(g, pc_name)
                        if not new_role:
                            try:
                                new_role = await g.create_role(name=role_name)
                            except:
                                print("ロール作成に失敗")
                                return
                        if not new_pc:
                            try:
                                overwrites = {
                                    g.default_role: discord.PermissionOverwrite(read_messages=False),
                                    g.me: discord.PermissionOverwrite(read_messages=True),
                                    new_role: discord.PermissionOverwrite(read_messages=True, manage_channels=False, manage_messages=False)
                                }
                                new_pc = await g.create_text_channel(name=pc_name, overwrites=overwrites, category=vc.category)
                                message = await new_pc.send("全員が退出するとこのテキストチャンネルは削除されます。")
                                await message.pin()
                            except Exception as e:
                                print(e)
                                print("テキストチャンネル作成に失敗")
                                return
                        for m in vc.members:
                            if not new_role in m.roles:
                                await m.add_roles(new_role)
                    except Exception as e:
                        print(e)
                        print("初期化処理に失敗")
                        return
                if len(vc.members) > 0:
                    await create_PC(vc)


def setup(bot):
    bot.add_cog(PrivateRoomCog(bot))