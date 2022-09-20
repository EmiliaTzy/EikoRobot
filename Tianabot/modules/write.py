from pyrogram import filters

from Tianabot import pbot


@pbot.on_message(filters.command("write"))
async def handwriting(_, message):
    if len(message.command) < 2:
        return await message.reply_text("» Berikan beberapa teks untuk menulisnya di salinan saya...")
    m = await message.reply_text("» Tunggu sebentar, saya masih menulis teks itu...")
    name = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    hand = "https://apis.xditya.me/write?text=" + name
    await m.edit("Mengunggah...")
    await pbot.send_chat_action(message.chat.id, "upload_photo")
    await message.reply_photo(hand, caption="Tulisan dari [Eiko](t.me/EikoManager_Bot)")
