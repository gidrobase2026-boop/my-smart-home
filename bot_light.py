import telebot
from telebot import types
import requests

BOT_TOKEN = "8807588104:AAGSkYZFY09tDIxH9AeTWA7-hZgNoccgqnE" 
YANDEX_TOKEN = "y0__wgBEJDHqYoHGMm-TSCKu8vBGRwXuS2q1hTRZaEcIT7SXMsXD03D"

bot = telebot.TeleBot(BOT_TOKEN)
HEADERS = {"Authorization": f"Bearer {YANDEX_TOKEN}", "Content-Type": "application/json"}

DEVICES = {"bathroom": "9c83c00d-5630-41fc-975a-3646edd404d3"}
SCENARIOS = {
    "hall_on": "56c4286b-0b82-42f1-adc1-8c8e584535b5",
    "hall_off": "6ba04779-f3a0-42f2-b101-6db6eac7032e",
    "corridor_on": "540bffbc-cf97-41b3-99f3-597b1dfa665d",
    "corridor_off": "947c5244-6e75-42c4-a6b7-c993180503d9",
    "camera_on": "722d2178-e408-40a3-9c4d-8f0813ac8aba",
    "camera_off": "b969fce4-09fd-42bf-9666-2b195fc01eff"
}

def run_action(scenario_id):
    return requests.post(f"https://api.iot.yandex.net/v1.0/scenarios/{scenario_id}/actions", headers=HEADERS, json={}).status_code == 200

def send_device(device_id, val):
    payload = {"devices": [{"id": device_id, "actions": [{"type": "devices.capabilities.on_off", "state": {"instance": "on", "value": val}}]}]}
    return requests.post("https://api.iot.yandex.net/v1.0/devices/actions", headers=HEADERS, json=payload).status_code == 200

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💡 Зал Вкл", callback_data="hall_on"), types.InlineKeyboardButton("🌑 Зал Выкл", callback_data="hall_off"),
        types.InlineKeyboardButton("💡 Коридор Вкл", callback_data="corridor_on"), types.InlineKeyboardButton("🌑 Коридор Выкл", callback_data="corridor_off"),
        types.InlineKeyboardButton("💡 Ванная Вкл", callback_data="bathroom_on"), types.InlineKeyboardButton("🌑 Ванная Выкл", callback_data="bathroom_off"),
        types.InlineKeyboardButton("📹 Камера Вкл", callback_data="camera_on"), types.InlineKeyboardButton("📹 Камера Выкл", callback_data="camera_off")
    )
    bot.send_message(message.chat.id, "⚡ **Пульт Света и Камер:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data
    if data.startswith("bathroom"):
        send_device(DEVICES["bathroom"], data.endswith("_on"))
        bot.answer_callback_query(call.id, "✅ Ванная!")
    elif data in SCENARIOS:
        run_action(SCENARIOS[data])
        bot.answer_callback_query(call.id, "✅ Готово!")

print("Электрик запущен...")
bot.infinity_polling()