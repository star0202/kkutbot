from datetime import datetime

import discord

from tools.db import db

from .config import config  # noqa


class ConfirmSendAnnouncement(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='전송하기', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa
        self.value = True
        await interaction.response.send_message("공지 전송 완료!")
        self.stop()

    @discord.ui.button(label='취소하기', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa
        self.value = False
        await interaction.response.send_message("공지 전송이 취소되었습니다.")
        self.stop()


class AnnouncementInput(discord.ui.Modal, title='공지 작성하기'):
    a_title = discord.ui.TextInput(label='공지 제목', required=True)
    description = discord.ui.TextInput(label='공지 본문', style=discord.TextStyle.long, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"**{interaction.user.name}** 님의 메일함",
            description="> 1주일간 읽지 않은 메일 `1` 개",
            color=config('colors.help')
        )
        embed.add_field(name=f"{self.a_title.value} - `1초 전`", value=self.description.value)
        view = ConfirmSendAnnouncement()
        await interaction.response.send_message("**<공지 미리보기>**", embed=embed, view=view)
        await view.wait()
        if view.value:
            await db.user.update_many(
                {},
                {
                    '$push': {'mails': {'title': self.a_title.value, 'value': self.description.value, 'time': datetime.now()}},
                    '$set': {'alerts.mails': False}
                }
            )


class SendAnnouncement(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='내용 작성하기', style=discord.ButtonStyle.blurple)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa
        await interaction.response.send_modal(AnnouncementInput(timeout=120))
        self.value = True
        self.stop()


class ConfirmSendNotice(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='전송하기', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa
        self.value = True
        await interaction.response.send_message("알림 전송 완료!")
        self.stop()

    @discord.ui.button(label='취소하기', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa
        self.value = False
        await interaction.response.send_message("알림 전송이 취소되었습니다.")
        self.stop()


class NoticeInput(discord.ui.Modal, title='알림 보내기'):
    msg = discord.ui.TextInput(label='알림 내용', style=discord.TextStyle.long, required=True)

    def __init__(self, timeout: float, target: int):
        super().__init__(timeout=timeout)
        self.value = None
        self.target = target

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"**{interaction.user.name}** 님의 메일함",
            description="> 1주일간 읽지 않은 메일 `1` 개",
            color=config('colors.help')
        )
        embed.add_field(name=f"관리자로부터의 알림 - `1초 전`", value=self.msg.value)
        view = ConfirmSendNotice()
        await interaction.response.send_message("**<알림 미리보기>**", embed=embed, view=view)
        await view.wait()
        if view.value:
            await db.user.update_one(
                {'_id': self.target},
                {
                    '$push': {'mail': {'title': "관리자로부터의 알림", 'value': self.msg.value, 'time': datetime.now()}},
                    '$set': {'alert.mail': False}
                }
            )


class SendNotice(discord.ui.View):
    def __init__(self, target: int):
        super().__init__()
        self.value = None
        self.target = target

    @discord.ui.button(label='내용 작성하기', style=discord.ButtonStyle.blurple)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa
        await interaction.response.send_modal(NoticeInput(timeout=120, target=self.target))
        self.value = True
        self.stop()
