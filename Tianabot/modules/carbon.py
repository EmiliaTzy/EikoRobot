from pyrogram.types import Message
from pyrogram import filters
from Tianabot import pbot
from Tianabot.utils.errors import capture_err
from asyncio import gather
from io import BytesIO
from Tianabot import aiohttpsession as aiosession

async def make_carbon(code):
    url = "https://carbonara.vercel.app/api/cook"
    async with aiosession.post(url, json={"code": code}) as resp:
        image = BytesIO(await resp.read())
    image.name = "carbon.png"
    return image

@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if not message.reply_to_message:
        return await message.reply_text("`Balas ke pesan untuk menghasilkan carbon.`")
    if not message.reply_to_message.text:
        return await message.reply_text("`Balas ke pesan untuk menghasilkan carbon.`")
    m = await message.reply_text("`Menghasilkan Carbon...`")
    carbon = await make_carbon(message.reply_to_message.text)
    await m.edit("`Mengunggah Carbon...`")
    await pbot.send_photo(message.chat.id, carbon)
    await m.delete()
    carbon.close()
