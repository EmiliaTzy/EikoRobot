import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler, run_async
from telegram.utils.helpers import mention_html

import Tianabot.modules.sql.approve_sql as sql
from Tianabot import DRAGONS, dispatcher
from Tianabot.modules.disable import DisableAbleCommandHandler
from Tianabot.modules.helper_funcs.chat_status import user_admin
from Tianabot.modules.helper_funcs.extraction import extract_user
from Tianabot.modules.log_channel import loggable


@loggable
@user_admin
@run_async
def approve(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "Saya tidak tahu siapa yang Anda bicarakan, Anda harus menentukan pengguna!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text(
            "Pengguna sudah menjadi admin - kunci, daftar blokir, dan antiflood sudah tidak berlaku untuk mereka."
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) telah disetujui dalam {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.approve(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) telah disetujui dalam {chat_title}! Mereka sekarang akan diabaikan oleh tindakan admin otomatis seperti kunci, daftar blokir, dan antiflood.",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#DISETUJUI\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Pengguna:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@loggable
@user_admin
@run_async
def disapprove(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "Saya tidak tahu siapa yang Anda bicarakan, Anda harus menentukan pengguna!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text("Pengguna ini adalah admin, mereka tidak dapat ditolak.")
        return ""
    if not sql.is_approved(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} belum disetujui!")
        return ""
    sql.disapprove(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} tidak lagi disetujui dalam {chat_title}."
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#DITOLAK\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Pengguna:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
@run_async
def approved(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "Pengguna berikut disetujui.\n"
    approved_users = sql.list_approved(message.chat_id)
    for i in approved_users:
        member = chat.get_member(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("approved.\n"):
        message.reply_text(f"Tidak ada pengguna yang disetujui dalam {chat_title}.")
        return ""
    else:
        message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@user_admin
@run_async
def approval(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text(
            "Saya tidak tahu siapa yang Anda bicarakan, Anda harus menentukan pengguna!"
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"{member.user['first_name']} adalah pengguna yang disetujui. Kunci, antiflood, dan daftar blokir tidak akan berlaku untuk mereka."
        )
    else:
        message.reply_text(
            f"{member.user['first_name']} bukan pengguna yang disetujui. Mereka dipengaruhi oleh perintah normal."
        )


@run_async
def unapproveall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "Hanya pemilik obrolan yang dapat membatalkan persetujuan semua pengguna sekaligus."
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Batalkan persetujuan semua pengguna", callback_data="unapproveall_user"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Batal", callback_data="unapproveall_cancel"
                    )
                ],
            ]
        )
        update.effective_message.reply_text(
            f"Apakah Anda yakin ingin membatalkan persetujuan semua pengguna di {chat.title}? Tindakan ini tidak bisa dibatalkan.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


@run_async
def unapproveall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)

        if member.status == "administrator":
            query.answer("Hanya pemilik obrolan yang dapat melakukan ini.")
        if member.status == "member":
            query.answer("Anda harus menjadi admin untuk melakukan ini.")
    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            message.edit_text("Penghapusan semua pengguna yang disetujui telah dibatalkan.")
            return ""
        if member.status == "administrator":
            query.answer("Hanya pemilik obrolan yang dapat melakukan ini.")
        if member.status == "member":
            query.answer("Anda harus menjadi admin untuk melakukan ini.")


__help__ = """
Terkadang, Anda mungkin memercayai pengguna untuk tidak mengirim konten yang tidak diinginkan.

Mungkin tidak cukup untuk menjadikannya admin, tetapi Anda mungkin baik-baik saja dengan kunci, daftar hitam, dan antibanjir yang tidak berlaku untuk mereka.
Untuk itulah persetujuan - setujui pengguna yang dapat dipercaya untuk memungkinkan mereka mengirim

*Perintah Admin:*
❍ /approval*:* Periksa status persetujuan pengguna dalam obrolan ini.
❍ /approve*:* Menyetujui pengguna. Kunci, daftar hitam, dan antibanjir tidak akan berlaku lagi.
❍ /unapprove*:* Tidak menyetujui pengguna. Mereka sekarang akan dikenakan kunci, daftar hitam, dan antibanjir lagi.
❍ /approved*:* Daftar semua pengguna yang disetujui.
❍ /unapproveall*:* Batalkan persetujuan *SEMUA* pengguna dalam obrolan. Ini tidak dapat dibatalkan.
"""

APPROVE = DisableAbleCommandHandler("approve", approve)
DISAPPROVE = DisableAbleCommandHandler("unapprove", disapprove)
APPROVED = DisableAbleCommandHandler("approved", approved)
APPROVAL = DisableAbleCommandHandler("approval", approval)
UNAPPROVEALL = DisableAbleCommandHandler("unapproveall", unapproveall)
UNAPPROVEALL_BTN = CallbackQueryHandler(unapproveall_btn, pattern=r"unapproveall_.*")

dispatcher.add_handler(APPROVE)
dispatcher.add_handler(DISAPPROVE)
dispatcher.add_handler(APPROVED)
dispatcher.add_handler(APPROVAL)
dispatcher.add_handler(UNAPPROVEALL)
dispatcher.add_handler(UNAPPROVEALL_BTN)

__mod_name__ = "𝙿𝚎𝚛𝚜𝚎𝚝𝚞𝚓𝚞𝚊𝚗 👮🏻‍♂"
__command_list__ = ["approve", "unapprove", "approved", "approval"]
__handlers__ = [APPROVE, DISAPPROVE, APPROVED, APPROVAL]
