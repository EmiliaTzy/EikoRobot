import importlib
import time
import re
from sys import argv
from typing import Optional
import Tianabot.modules.sql.users_sql as sql

from Tianabot import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    BOT_TUT,
    MUSICBOT_TUT,
    UPDATE_CHANNEL,
    BOT_USERNAME,
    BOT_NAME,
    ASS_USERNAME,
    START_IMG,
    TOKEN,
    URL,
    OWNER_USERNAME,
    WEBHOOK,
    SUPPORT_CHAT,
    dispatcher,
    StartTime,
    telethn,
    pbot,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from Tianabot.modules import ALL_MODULES
from Tianabot.modules.helper_funcs.chat_status import is_user_admin
from Tianabot.modules.helper_funcs.misc import paginate_modules
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time



PM_START_TEXT = """
*Halo {} * [!]({})
───────────────────────
× *Saya Adalah Bot Untuk Mengatur Grupmu*
× *Saya Sangat Cepat dan Lebih efisien, Saya menyediakan fitur luar biasa!*
───────────────────────
× *Waktu Operasi Server:* `{}`
× `{}` *Pengguna, Lintas* `{}` *Obrolan.*
───────────────────────"""

buttons = [
    [
        InlineKeyboardButton(text="❓ 𝗣𝗲𝗿𝗶𝗻𝘁𝗮𝗵 & 𝗕𝗮𝗻𝘁𝘂𝗮𝗻 ❗️", callback_data="tiana_"),
    ],
    [
        InlineKeyboardButton(text="👩‍💻 𝙄𝙣𝙛𝙤", callback_data="about_"),
        InlineKeyboardButton(text="𝙊𝙬𝙣𝙚𝙧 👨‍✈️", url=f"https://t.me/{OWNER_USERNAME}"),
    ],
   [
        InlineKeyboardButton(text="📇 𝙐𝙥𝙙𝙖𝙩𝙚𝙨", url=f"http://t.me/{UPDATE_CHANNEL}"),
        InlineKeyboardButton(text="𝙎𝙪𝙥𝙥𝙤𝙧𝙩 🫂", url=f"https://t.me/{SUPPORT_CHAT}"),
    ],
    [  
        InlineKeyboardButton(text="➕️ 𝗧𝗮𝗺𝗯𝗮𝗵𝗸𝗮𝗻 𝘀𝗮𝘆𝗮 𝗸𝗲 𝗴𝗿𝘂𝗽𝗺𝘂 ➕️", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
    ], 
    
]

TIANA_IMG = f"{START_IMG}"
TIANA_VIDA = f"{BOT_TUT}"
TIANA_VIDB = f"{MUSICBOT_TUT}"

HELP_STRINGS = """*Klik tombol dibawah ini untuk mendapatkan dokumentasi tentang spesifikasi Modul*"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("Tianabot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__sub_mod__") and imported_module.__sub_mod__:
        SUB_MODE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


@run_async
def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


@run_async
def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="⬅️ KEMBALI", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_sticker(
                "CAACAgEAAxkDA3MOMWMkRqKBvnxK-e-sXq0dl1OZU6ZlAAK4AwACU2QgRek8SEbDG5jFKQQ"
            update.effective_message.reply_text(
                PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
        else:    
            first_name = update.effective_user.first_name
            update.effective_message.reply_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    START_IMG,
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats()),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
          first_name = update.effective_user.first_name
          update.effective_message.reply_photo(
                TIANA_IMG, caption="""*Hallo {} !*
───────────────────
× *Saya Adalah Bot Untuk Mengatur Grupmu*
× *Saya Sangat Cepat dan Lebih efisien, Saya menyediakan fitur luar biasa!*
───────────────────
× *Waktu Operasi Server:* `{}`
× `{}` *Pengguna, Lintas* `{}` *Obrolan.*
───────────────────""".format(
                    escape_markdown(first_name),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats()),
                reply_markup=InlineKeyboardMarkup(
                 [
                  [InlineKeyboardButton(text="📄 Sumber Kode", url="https://youtube.com"), 
                   InlineKeyboardButton(text="🫂 Support", url=f"https://t.me/{SUPPORT_CHAT}")]
                 ]
              ),
                parse_mode=ParseMode.MARKDOWN,              
            )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "「 Bantuan Dari *{}* 」:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="「 𝐾𝑒𝑚𝑏𝑎𝑙𝑖 」", callback_data="help_back")]]
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


@run_async
def tiana_callback_handler(update, context):
    query = update.callback_query
    if query.data == "tiana_":
        query.message.edit_text(
            text="""𝗦𝗲𝗹𝗮𝗺𝗮𝘁 𝗗𝗮𝘁𝗮𝗻𝗴 𝗗𝗶 𝗠𝗲𝗻𝘂 𝗕𝗮𝗻𝘁𝘂𝗮𝗻. 
────────────────────────
*Pilih semua perintah untuk bantuan penuh atau pilih kategori untuk dokumentasi bantuan lebih lanjut di bidang yang dipilih*""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                     InlineKeyboardButton(text="➕ 𝗦𝗲𝗺𝘂𝗮 𝗣𝗲𝗿𝗶𝗻𝘁𝗮𝗵 ➕", callback_data="help_back"),
                    ],                           
                    [InlineKeyboardButton(text="𝗕𝗮𝗴𝗮𝗶𝗺𝗮𝗻𝗮 𝗰𝗮𝗿𝗮 𝗺𝗲𝗻𝗴𝗴𝘂𝗻𝗮𝗸𝗮𝗻 𝘀𝗮𝘆𝗮 ❓", callback_data="tiana_help"),
                     InlineKeyboardButton(text="𝗕𝗼𝘁 𝗠𝘂𝘀𝗶𝗸 🎧", callback_data="tiana_music")],
                    [InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="tiana_back"),
                     InlineKeyboardButton(text="𝙄𝙣𝙡𝙞𝙣𝙚 🔗", switch_inline_query_current_chat="")],
                ]
            ),
        )
    elif query.data == "tiana_back":
        first_name = update.effective_user.first_name
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    START_IMG,
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats()),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )
    elif query.data == "tiana_help":
        query.message.edit_text(
            text=f"""*Baru Untuk {BOT_NAME}! Berikut adalah panduan memulai cepat yang akan membantu Anda memahami apa itu {BOT_NAME} dan bagaimana cara menggunakannya.

Klik tombol di bawah ini untuk menambahkan bot di grup Anda. Penjelasan dasar mulai tahu tentang cara menggunakan saya*""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
              [[InlineKeyboardButton(text="𝙎𝙚𝙩𝙪𝙥 𝙏𝙪𝙩𝙤𝙧𝙞𝙖𝙡 🎥", callback_data="tiana_vida")],
               [InlineKeyboardButton(text="➕️ 𝗧𝗮𝗺𝗯𝗮𝗵𝗸𝗮𝗻 𝘀𝗮𝘆𝗮 𝗸𝗲 𝗴𝗿𝘂𝗽𝗺𝘂 ➕️", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],       
                [InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="tiana_"),
                 InlineKeyboardButton(text="➡️", callback_data="tiana_helpa")]
              ]
            ),
        )
    elif query.data == "tiana_helpa":
        query.message.edit_text(
            text=f"""<b>Hai, Selamat datang di tutorial konfigurasi

Sebelum kita pergi, saya perlu izin admin di obrolan ini agar berfungsi dengan baik.
1). Klik Management Grup.
2). Pergi Ke Administrator Dan Tambahkan @EikoManager_Bot Sebagai Admin.
3). Berikan Semua Hal Penuh Untuk Eiko Kecuali Anonim</b>""",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
              [[InlineKeyboardButton(text="⬅️", callback_data="tiana_help"),
                InlineKeyboardButton(text="➡️", callback_data="tiana_helpb")],               
              ]
            ),
        )
    elif query.data == "tiana_helpb":
        query.message.edit_text(
            text="""*Selamat, bot ini sekarang siap untuk mengelola grup Anda

Berikut adalah beberapa hal penting untuk dicoba di eiko

×  Alat admin
Alat admin dasar membantu Anda, melindungi, dan memperkuat grup Anda
Anda dapat memblokir anggota, menendang anggota, mempromosikan sebagai admin melalui perintah bot
 
×  Selamat datang
Mari kita atur pesan selamat datang untuk pengguna baru yang datang ke grup Anda
Kirim /setwelcome (pesan) untuk mengatur pesan selamat datang
Anda juga dapat berhenti memasukkan robot atau spammer ke obrolan Anda dengan menyetel captcha selamat datang

Lihat menu bantuan untuk melihat semuanya secara detail*""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
              [
                [InlineKeyboardButton(text="⬅️", callback_data="tiana_helpa"),
                 InlineKeyboardButton(text="➡️", callback_data="tiana_helpc")]
                ]
            ),
        )
    elif query.data == "tiana_helpc":
        query.message.edit_text(
            text="""*× Filter
Filter dapat digunakan sebagai balasan/larangan/penghapusan otomatis ketika seseorang menggunakan kata atau kalimat
Misalnya jika saya memfilter kata 'halo' dan mengatur balasan sebagai 'hai'
Bot akan membalas sebagai 'hai' ketika seseorang mengatakan 'halo'
Anda dapat menambahkan filter dengan mengirimkan /filter Nama filter

× Chatbot AI
Ingin seseorang mengobrol dalam grup?
Eiko memiliki chatbot cerdas dengan dukungan multilang mari kita coba,
Kirim /chatbot on dan balas pesan saya untuk melihat keajaibannya*""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
              [
                [InlineKeyboardButton(text="⬅️", callback_data="tiana_helpb"),
                 InlineKeyboardButton(text="➡️", callback_data="tiana_helpd")]
                ]
            ),
        )
    elif query.data == "tiana_helpd":
        query.message.edit_text(
            text="""*× Menyiapkan catatan
Anda dapat menyimpan pesan/media/audio atau apa pun sebagai catatan menggunakan /notes
Untuk mendapatkan catatan cukup gunakan # di awal kata
Lihat gambarnya

× Menyiapkan mode malam
Anda dapat mengatur mode malam menggunakan perintah /nightmode on/off.
Catatan - obrolan mode malam ditutup secara otomatis pada pukul 00.00 dan dibuka secara otomatis pada pukul 06.00 untuk mencegah spam malam hari.*""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
              [
                [InlineKeyboardButton(text="⬅️", callback_data="tiana_helpc"),
                 InlineKeyboardButton(text="➡️", callback_data="tiana_helpe")]
                ]
            ),
        )
    elif query.data == "tiana_term":
        query.message.edit_text(
            text=f"""✗ *Syarat dan ketentuan:*

- Hanya nama depan, nama belakang (jika ada) dan nama pengguna (jika ada) yang disimpan untuk komunikasi yang nyaman!
- Tidak ada ID grup atau pesannya disimpan, kami menghormati privasi semua orang.
- Pesan antara Bot dan Anda hanya ada di depan mata Anda dan tidak ada gunanya kembali.
- Perhatikan grup Anda, jika seseorang mengirim spam ke grup Anda, Anda dapat menggunakan fitur laporan Klien Telegram Anda.
- Jangan spam perintah, tombol, atau apa pun di bot PM.

*CATATAN:* Syarat dan ketentuan bisa berubah sewaktu-waktu""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
              [InlineKeyboardButton(text="𝙐𝙥𝙙𝙖𝙩𝙚", url=f"https://t.me/{UPDATE_CHANNEL}"),       
              InlineKeyboardButton(text="𝙎𝙪𝙥𝙥𝙤𝙧𝙩", url=f"https://t.me/{SUPPORT_CHAT}")],       
              [InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="about_")]]
            ),
        )
    elif query.data == "tiana_helpe":
        query.message.edit_text(
            text="""*× Jadi sekarang Anda berada di akhir penjelasan dasar. Tapi ini tidak semua yang bisa saya lakukan.

Kirim /Help dalam pm untuk mengakses menu bantuan
Ada banyak alat praktis untuk dicoba.  
Dan juga jika Anda memiliki saran tentang saya, jangan lupa untuk memberi tahu mereka kepada developer

Terimakasih Lagi telah menggunakan saya

× Dengan menggunakan bot ini Anda menyetujui syarat & ketentuan kami*""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="➕ 𝗦𝗲𝗺𝘂𝗮 𝗣𝗲𝗿𝗶𝗻𝘁𝗮𝗵 ➕", callback_data="help_back")],
                [InlineKeyboardButton(text="⬅️ 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="tiana_helpd"),
                InlineKeyboardButton(text="𝗠𝗲𝗻𝘂 𝗨𝘁𝗮𝗺𝗮", callback_data="tiana_")]]
            ),
        )
    elif query.data == "tiana_music":
        query.message.edit_text(
            text=f"""* Berikut adalah bantuan untuk modul「Asisten」:*
            
1.) pertama, tambahkan saya ke grup Anda.
            
2.) kemudian promosikan saya sebagai admin dan berikan semua izin kecuali admin anonim.
            
3.) tambahkan Asisten ke grup Anda menggunakan secara manual untuk grup private.
            
4.) nyalakan obrolan video terlebih dahulu sebelum mulai memutar musik.
            
*Mari Nikmati Bot Musik Dan Bergabunglah dengan Grup Dukungan*""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
               [[InlineKeyboardButton(text="𝙎𝙚𝙩𝙪𝙥 𝙏𝙪𝙩𝙤𝙧𝙞𝙖𝙡 🎥", callback_data="tiana_vidb")],
                [InlineKeyboardButton(text="𝗣𝗲𝗿𝗶𝗻𝘁𝗮𝗵 𝙋𝙡𝙖𝙮", callback_data="tiana_musica"),
                 InlineKeyboardButton(text="𝗣𝗲𝗿𝗶𝗻𝘁𝗮𝗵 𝘽𝙤𝙩", callback_data="tiana_musicc")],
                [InlineKeyboardButton(text="𝗣𝗲𝗿𝗶𝗻𝘁𝗮𝗵 𝘼𝙙𝙢𝙞𝙣", callback_data="tiana_musicb"),
                 InlineKeyboardButton(text="𝗣𝗲𝗿𝗶𝗻𝘁𝗮𝗵 𝙀𝙭𝙩𝙧𝙖", callback_data="tiana_musicd")],
                [InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="tiana_")]
               ]
            ),
        )
    elif query.data == "tiana_musica":
        query.message.edit_text(
            text="""✗ *Berikut adalah bantuan untuk Perintah Play*:

*Catatan*: Eiko Music Bot bekerja pada satu perintah gabungan untuk Musik dan Video

✗ *File Youtube dan Telegram*:

/play [Balas ke Video atau Audio] atau [YT Link] atau [Nama Musik]  
- Streaming Video atau Musik di Obrolan Suara dengan memilih Tombol sebaris yang Anda dapatkan

✗ *Daftar Putar Tersimpan Database Eiko*:

/playlist 
- Periksa Daftar Putar Tersimpan Anda Di Server.

/deleteplaylist
- Hapus semua musik yang disimpan di daftar putar Anda

/playplaylist 
- Mulai mainkan Daftar Putar Tersimpan Anda di Server Eiko.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="tiana_music")]]
            ),
        )
    elif query.data == "tiana_musicb":
        query.message.edit_text(
            text="""✗ *Berikut adalah bantuan untuk Perintah Admin*:


✗ *Perintah Admin*:

/pause 
- Jeda pemutaran musik di obrolan suara.

/resume
- Lanjutkan musik yang dijeda di obrolan suara.

/skip
- Lewati musik yang sedang diputar di obrolan suara

/end or /stop
- Menghentikan Lagu.


✗ *Daftar Pengguna Resmi*:

Eiko memiliki fitur tambahan untuk pengguna non-admin yang ingin menggunakan perintah admin
-Pengguna auth dapat skip, pause, stop, resume Obrolan Suara bahkan tanpa Hak Admin.


/auth [Balas ke pesan atau Username] 
- Tambahkan pengguna ke AUTH LIST grup.

/unauth [Balas ke pesan atau Username] 
- Hapus pengguna dari AUTH LIST grup.

/authusers 
- Periksa DAFTAR AUTH grup.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="tiana_music")]]
            ),
        )
    elif query.data == "tiana_musicc":
        query.message.edit_text(
            text="""✗ *Inilah bantuan untuk Perintah Bot*:

/mstart 
- Mulai Eiko Music Bot.

/mhelp 
- Dapatkan Menu Pembantu Perintah dengan penjelasan rinci tentang perintah.

/msettings 
- Dapatkan dasbor Pengaturan grup. Anda dapat mengelola Mode Pengguna Auth. Mode Perintah dari sini.

/ping
- Ping Bot dan periksa statistik Ram, Cpu dll dari Eiko.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="tiana_music")]]
            ),
        )
    elif query.data == "tiana_musicd":
        query.message.edit_text(
            text="""✗ *Berikut adalah bantuan untuk Perintah Ekstra*:

/lyrics atau /lirik [Nama Lagu]
- Mencari Lirik untuk Musik tertentu di web.

/sudolist 
- Periksa Sudo Pengguna Eiko Music Bot

/song [Nama Lagu] or [YT Link]
- Unduh lagu apa pun dari youtube dalam format mp3 atau mp4 melalui Eiko.

/queue
- Periksa Daftar Antrian Musik.

/cleanmode [Enable|Disable]
- Saat diaktifkan, Eiko akan menghapus pesan terakhirnya yang ketiga untuk menjaga obrolan Anda tetap bersih.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="tiana_music")]]
            ),
        )
    elif query.data == "tiana_about":
        query.message.edit_text(
            text=f"""Eiko Telah aktif sejak Juli 2022 dan terus diperbarui!!           

Bot Admin
                       
• [Az](https://t.me/tth_kiya98) penerjemah bot dan pengembang utama.            
• Seorang Fotografer sekaligus mahasiswa Universitas Al Azhar Cairo Mesir.
            
Support            
• [Klik Disini](https://t.me/CatatanAzDay) untuk berkonsultasi dengan daftar Suporter Resmi bot yang diperbarui.            
• Terima kasih kepada semua donor kami untuk mendukung server dan biaya pengembangan dan semua orang yang telah melaporkan bug atau menyarankan fitur baru.           
• Kami juga berterima kasih kepada semua grup yang mengandalkan Bot kami untuk layanan ini, kami harap Anda akan selalu menyukainya: kami terus bekerja untuk meningkatkannya""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="about_")]]
            ),
        )
    elif query.data == "tiana_support":
        query.message.edit_text(
            text=f"*{BOT_NAME} Support Chats*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="𝐁𝐞𝐫𝐢𝐭𝐚", url=f"t.me/{UPDATE_CHANNEL}"),
                    InlineKeyboardButton(text="𝐃𝐨𝐧𝐚𝐬𝐢 𝐊𝐞 𝐒𝐚𝐲𝐚", url=f"{DONATION_LINK}"),
                 ],
                 [
                    InlineKeyboardButton(text="𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=f"t.me/{SUPPORT_CHAT}"),
                    InlineKeyboardButton(text="𝐏𝐞𝐦𝐛𝐚𝐡𝐚𝐫𝐮𝐚𝐧", url=f"https://t.me/{UPDATE_CHANNEL}"),
                 ],
                 [
                    InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="about_"),
                 
                 ]
                ]
            ),
        )
    elif query.data == "tiana_source":
        query.message.edit_text(
            text="""*EikoRobot Sekarang Proyek Bot Sumber Terbuka.*

*Klik Tombol di bawah ini untuk Mendapatkan Kode Sumber.*""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="📄 𝗦𝘂𝗺𝗯𝗲𝗿", url="github.com"),                 
                    InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="about_"),
                 ]    
                ]
            ),
        )
    elif query.data == "tiana_vida":
        query.message.reply_video(
            TIANA_VIDA,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,           
        )
    elif query.data == "tiana_vidb":
        query.message.reply_video(
            TIANA_VIDB,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,           
        )
        
@run_async
def tiana_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "about_":
        query.message.edit_text(
            text="""𝗞𝗹𝗶𝗸 𝗧𝗼𝗺𝗯𝗼𝗹 𝗨𝗻𝘁𝘂𝗸 𝗧𝗮𝗵𝘂 𝗟𝗲𝗯𝗶𝗵 𝗕𝗮𝗻𝘆𝗮𝗸 𝗧𝗲𝗻𝘁𝗮𝗻𝗴 𝗦𝗮𝘆𝗮""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
               [
                 [
                     InlineKeyboardButton(text="❗️ 𝗧𝗲𝗻𝘁𝗮𝗻𝗴 𝗦𝗮𝘆𝗮", callback_data="tiana_about"),
                     InlineKeyboardButton(text="📄 𝗦𝘂𝗺𝗯𝗲𝗿", callback_data="tiana_source"),
                 ],
                 [  
                    InlineKeyboardButton(text="🫂 𝙎𝙪𝙥𝙥𝙤𝙧𝙩", callback_data="tiana_support"),
                    InlineKeyboardButton(text="👨‍✈️ 𝙊𝙬𝙣𝙚𝙧", url=f"t.me/{OWNER_USERNAME}"),
                 ],
                 [
                     InlineKeyboardButton(text="𝗦𝘆𝗮𝗿𝗮𝘁 𝗱𝗮𝗻 𝗞𝗲𝘁𝗲𝗻𝘁𝘂𝗮𝗻❗️", callback_data="tiana_term"),
                 ],
                 [
                     InlineKeyboardButton(text="🔙 𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="about_back"),
                 ]    
               ]
            ),
        )
    elif query.data == "about_back":
        first_name = update.effective_user.first_name
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    START_IMG,
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats()),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )

@run_async
def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Hubungi saya di PM untuk mendapatkan bantuan {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="𝗕𝗮𝗻𝘁𝘂𝗮𝗻",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "Hubungi saya di PM untuk mendapatkan daftar kemungkinan perintah.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝗕𝗮𝗻𝘁𝘂𝗮𝗻",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Berikut adalah bantuan yang tersedia untuk modul *{}*:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="𝗞𝗲𝗺𝗯𝗮𝗹𝗶", callback_data="tiana_")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "Ini adalah pengaturan Anda saat ini:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Sepertinya tidak ada pengaturan khusus pengguna yang tersedia :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Modul mana yang ingin Anda periksa untuk setelan {}?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Sepertinya tidak ada pengaturan obrolan yang tersedia :'(\nKirim ini "
                "dalam obrolan grup Anda menjadi admin untuk menemukan pengaturannya saat ini!",
                parse_mode=ParseMode.MARKDOWN,
            )


@run_async
def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* memiliki pengaturan berikut untuk modul *{}*:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="𝗞𝗲𝗺𝗯𝗮𝗹𝗶",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hai! Ada beberapa setelan untuk {} - lanjutkan dan pilih yang "
                "kamu tertarik.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hai! Ada beberapa setelan untuk {} - lanjutkan dan pilih yang "
                "kamu tertarik.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hai! Ada beberapa setelan untuk {} - lanjutkan dan pilih yang "
                "kamu tertarik.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Klik di sini untuk mendapatkan pengaturan obrolan ini, serta pengaturan Anda."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Pengaturan",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Klik Disini Untuk Melihat Pengaturanmu."

    else:
        send_settings(chat.id, user.id, True)


@run_async
def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            text = "𝗔𝗻𝗱𝗮 𝗗𝗮𝗽𝗮𝘁 𝗗𝗼𝗻𝗮𝘀𝗶 𝗦𝗮𝘆𝗮 𝗗𝗶 𝗦𝗶𝗻𝗶", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(
               [
                 [                   
                    InlineKeyboardButton(text="𝐃𝐨𝐧𝐚𝐬𝐢 𝐊𝐞 𝐒𝐚𝐲𝐚", url=f"{DONATION_LINK}"),
                 ]
               ]
        )
    )
    else:
        try:
            bot.send_message(
                user.id,
                text = "𝗔𝗻𝗱𝗮 𝗗𝗮𝗽𝗮𝘁 𝗗𝗼𝗻𝗮𝘀𝗶 𝗦𝗮𝘆𝗮 𝗗𝗶 𝗦𝗶𝗻𝗶" ,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
               [
                 [                   
                    InlineKeyboardButton(text="𝐃𝐨𝐧𝐚𝐬𝐢 𝐊𝐞 𝐒𝐚𝐲𝐚", url=f"{DONATION_LINK}"),
                 ]
               ]
             )
            )

            update.effective_message.reply_text(
                "Saya telah PM Anda tentang menyumbang ke pemilik saya!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Hubungi saya di PM terlebih dahulu untuk mendapatkan informasi donasi."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Berhasil Migrasi!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@{SUPPORT_CHAT}", "𝐄𝐢𝐤𝐨 𝐁𝐨𝐭 𝐁𝐞𝐫𝐡𝐚𝐬𝐢𝐥 𝐃𝐢𝐩𝐞𝐫𝐛𝐚𝐫𝐮𝐢✅")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start)

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    about_callback_handler = CallbackQueryHandler(tiana_callback_handler, pattern=r"tiana_")
    Tiana_callback_handler = CallbackQueryHandler(tiana_about_callback, pattern=r"about_")
  
    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(Tiana_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Gunakan webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Berhasil Dimulai")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Berhasil Memuat Modul: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
