import os
from Tianabot import telethn as tbot
from geopy.geocoders import Nominatim
from Tianabot.events import register
from Tianabot import *
from telethon import *
from telethon.tl import *

GMAPS_LOC = "https://maps.googleapis.com/maps/api/geocode/json"


@register(pattern="^/gps (.*)")
async def _(event):
    args = event.pattern_match.group(1)

    try:
        geolocator = Nominatim(user_agent="SkittBot")
        location = args
        geoloc = geolocator.geocode(location)
        longitude = geoloc.longitude
        latitude = geoloc.latitude
        gm = "https://www.google.com/maps/search/{},{}".format(latitude, longitude)
        await tbot.send_file(
            event.chat_id,
            file=types.InputMediaGeoPoint(
                types.InputGeoPoint(float(latitude), float(longitude))
            ),
        )
        await event.reply(
            "Buka Dengan: [🌏Google Maps]({})".format(gm),
            link_preview=False,
        )
    except Exception as e:
        print(e)
        await event.reply("Saya Tidak Dapat Menemukan Itu")
