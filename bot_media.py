import telebot
from telebot import types
import requests

BOT_TOKEN = "8612532084:AAEI8xKLLl_hZ6eQTsXWkymjSehlApGn4TI" 
YANDEX_TOKEN = "y0__wgBEJDHqYoHGMm-TSCKu8vBGRwXuS2q1hTRZaEcIT7SXMsXD03D"

bot = telebot.TeleBot(BOT_TOKEN)
HEADERS = {"Authorization": f"Bearer {YANDEX_TOKEN}", "Content-Type": "application/json"}

DEVICES = {"station": "877a36f9-3aa6-49c9-9a8e-f75fd69ce978"}
SCENARIOS = {
    "tv_on": "e5a032eb-fc69-43d2-b2c4-757217bf0284",
    "tv_off": "e1c1d28e-604b-4f88-94d2-c530681cc0e8"
}

def run_scenario(sid):
    return requests.post(f"https://api.iot.yandex.net/v1.0/scenarios/{sid}/actions", headers=HEADERS, json={}).status_code == 200

def send_device(device_id, cap, inst=None, val=None):
    action = {"type": cap, "state": {}}
    if inst: action["state"]["instance"] = inst
    if val is not None: action["state"]["value"] = val
    payload = {"devices": [{"id": device_id, "actions": [action]}]}
    return requests.post("https://api.iot.yandex.net/v1.0/devices/actions", headers=HEADERS, json=payload).status_code == 200

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📺 ТВ Вкл", callback_data="tv_on"),
        types.InlineKeyboardButton("📺 ТВ Выкл", callback_data="tv_off"),
        types.InlineKeyboardButton("⏸️ Пауза", callback_data="station_pause"),
        types.InlineKeyboardButton("🔊 Громче", callback_data="station_vol_up")
    )
    bot.send_message(message.chat.id, "📺 **Медиа-пульт:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data
    if data in SCENARIOS:
        run_scenario(SCENARIOS[data])
        bot.answer_callback_query(call.id, "✅ ТВ готов!")
    elif data == "station_pause":
        send_device(DEVICES["station"], "devices.capabilities.toggle", "pause", True)
        bot.answer_callback_query(call.id, "⏸️ Пауза")
    elif data == "station_vol_up":
        send_device(DEVICES["station"], "devices.capabilities.range", "volume", 10)
        bot.answer_callback_query(call.id, "🔊 Громче")

print("Медиа-бот запущен...")
bot.infinity_polling()