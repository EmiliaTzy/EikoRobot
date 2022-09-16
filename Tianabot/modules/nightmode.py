import os
from Tianabot.modules.sql.night_mode_sql import (
    add_nightmode,
    rmnightmode,
    get_all_chat_id,
    is_nightmode_indb,
)
from telethon.tl.types import ChatBannedRights
from apscheduler.schedulers.asyncio import AsyncIOScheduler 
from telethon import functions
from Tianabot.events import register
from Tianabot import telethn as tbot, OWNER_ID
from telethon import Button, custom, events

hehes = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)

openhehe = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)

from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChatAdminRights,
    MessageEntityMentionName,
    MessageMediaPhoto,
)

from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)

async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True

async def can_change_info(message):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.change_info
    )

@register(pattern="^/(nightmode|Nightmode|NightMode|Nightmode|NIGHTMODE) ?(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    input = event.pattern_match.group(2)
    if not event.sender_id == OWNER_ID:
        if not await is_register_admin(event.input_chat, event.sender_id):
           await event.reply("Hanya Admin Yang Bisa Menjalankan Perintah Ini!")
           return
        else:
          if not await can_change_info(message=event):
            await event.reply("Anda kehilangan hak berikut untuk menggunakan perintah ini: Ubah Info Grup")
            return
    if not input:
        if is_nightmode_indb(str(event.chat_id)):
                await event.reply(
                    "Sekarang Mode Malam Dihidupkan Untuk Obrolan Ini"
                )
                return
        await event.reply(
            "Sekarang Mode Malam Dimatikan Untuk Obrolan Ini"
        )
        return
    if "on" in input:
        if event.is_group:
            if is_nightmode_indb(str(event.chat_id)):
                    await event.reply(
                        "Mode Malam Sudah Dihidupkan Untuk Obrolan Ini"
                    )
                    return
            add_nightmode(str(event.chat_id))
            await event.reply("Mode Malam Telah Dihidupkan Untuk Obrolan Ini.")
    if "off" in input:
        if event.is_group:
            if not is_nightmode_indb(str(event.chat_id)):
                    await event.reply(
                        "Mode Malam Sudah Dimatikan Untuk Obrolan Ini"
                    )
                    return
        rmnightmode(str(event.chat_id))
        await event.reply("Mode Malam Dimatikan!")
    if not "off" in input and not "on" in input:
        await event.reply("Mohon Masukkan kata kunci On atau Off!")
        return


async def job_close():
    chats = get_all_chat_id()
    if len(chats) == 0:
        return
    for pro in chats:
        try:
            await tbot.send_message(
              int(pro.chat_id), "Pukul 00:00, Grup Saat ini Ditutup Hingga Pukul 06:00. Mode Malam Dimulai ! \n**Diatur Oleh @EikoManager_Bot**"
            )
            await tbot(
            functions.messages.EditChatDefaultBannedRightsRequest(
                peer=int(pro.chat_id), banned_rights=hehes
            )
            )
        except Exception as e:
            logger.info(f"Tidak Dapat Menutup Grup {chat} - {e}")

#Run everyday at 12am
scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=59)
scheduler.start()

async def job_open():
    chats = get_all_chat_id()
    if len(chats) == 0:
        return
    for pro in chats:
        try:
            await tbot.send_message(
              int(pro.chat_id), "Pukul 06:00, Grup Telah Dibuka.\n**Diatur Oleh @EikoManager_Bot**"
            )
            await tbot(
            functions.messages.EditChatDefaultBannedRightsRequest(
                peer=int(pro.chat_id), banned_rights=openhehe
            )
        )
        except Exception as e:
            logger.info(f"Tidak Dapat Membuka Grup {pro.chat_id} - {e}")

# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
scheduler.add_job(job_open, trigger="cron", hour=5, minute=58)
scheduler.start()

__help__ = """
*Mode Malam*
❍ /nightmode (on/off) *:* Saat diaktifkan maka media akan dihapus. 
"""

__mod_name__ = "𝙼𝚘𝚍𝚎 𝙼𝚊𝚕𝚊𝚖 🌙"
