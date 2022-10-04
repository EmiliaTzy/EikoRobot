import os
import subprocess
import sys

from contextlib import suppress
from time import sleep

import Tianabot

from Tianabot import dispatcher
from Tianabot.modules.helper_funcs.chat_status import dev_plus
from telegram import TelegramError, Update
from telegram.error import Unauthorized
from telegram.ext import CallbackContext, CommandHandler, run_async

@run_async
@dev_plus
def allow_groups(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        update.effective_message.reply_text(f"Kondisi saat ini: {Tianabot.ALLOW_CHATS}")
        return
    if args[0].lower() in ["off", "no"]:
        Tianabot.ALLOW_CHATS = True
    elif args[0].lower() in ["yes", "on"]:
        Tianabot.ALLOW_CHATS = False
    else:
        update.effective_message.reply_text("Format: /lockdown Yes/No atau Off/On")
        return
    update.effective_message.reply_text("Done! Lockdown value toggled.")

@run_async
@dev_plus
def leave(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args
    if args:
        chat_id = str(args[0])
        try:
            bot.leave_chat(int(chat_id))
        except TelegramError:
            update.effective_message.reply_text(
                "Beep boop, Saya tidak bisa meninggalkan grup itu (tidak tahu mengapa)."
            )
            return
        with suppress(Unauthorized):
            update.effective_message.reply_text("Beep boop, Saya meninggalkan grup itu!.")
    else:
        update.effective_message.reply_text("Kirim ID obrolan yang valid")


@run_async
@dev_plus
def gitpull(update: Update, context: CallbackContext):
    sent_msg = update.effective_message.reply_text(
        "Menarik semua perubahan dari jarak jauh dan kemudian mencoba memulai kembali."
    )
    subprocess.Popen("git pull", stdout=subprocess.PIPE, shell=True)

    sent_msg_text = sent_msg.text + "\n\nPerubahan ditarik ... Saya kira .. Mulai ulang dalam"

    for i in reversed(range(5)):
        sent_msg.edit_text(sent_msg_text + str(i + 1))
        sleep(1)

    sent_msg.edit_text("Memulai Ulang.")

    os.system("restart.bat")
    os.execv("start.bat", sys.argv)


@run_async
@dev_plus
def restart(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "Memulai instance baru dan mematikan yang ini"
    )

    os.system("restart.bat")
    os.execv("start.bat", sys.argv)


LEAVE_HANDLER = CommandHandler("leave", leave)
GITPULL_HANDLER = CommandHandler("gitpull", gitpull)
RESTART_HANDLER = CommandHandler("reboot", restart)
ALLOWGROUPS_HANDLER = CommandHandler("lockdown", allow_groups)

dispatcher.add_handler(ALLOWGROUPS_HANDLER)
dispatcher.add_handler(LEAVE_HANDLER)
dispatcher.add_handler(GITPULL_HANDLER)
dispatcher.add_handler(RESTART_HANDLER)

__mod_name__ = "Evs"
__handlers__ = [LEAVE_HANDLER, GITPULL_HANDLER, RESTART_HANDLER, ALLOWGROUPS_HANDLER]
