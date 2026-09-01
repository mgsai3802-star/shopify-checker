# 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦: https://t.me/scriptdung
# 𝐁𝐚𝐜𝐤𝐮𝐩: https://t.me/scriptdungbackup
# 𝐃𝐞𝐯: @Xoarch (Stripe Telegram Bot)

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import aiohttp
import os
import random
from flask import Flask
from threading import Thread
import time

from api import process_card, parse_cc_string, extract_clean_response

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    print("Error: BOT_TOKEN ကို Render Environment တွင် မတွေ့ပါ။")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", threaded=True)
app = Flask(__name__)

ADMIN_ID = 1847021130
AUTHORIZED_USERS = {ADMIN_ID}

WORKING_KEYWORDS = [
    'card_declined', 'fraud', 'incorrect_zip', 'invalid_cvc', 'invalid_cvv',
    'insufficient_funds', 'approved', 'declined', 'incorrect_number', 'expired_card',
    'processing_error', 'call_issuer', 'try_again_later', 'fraudulent', 'security_violation'
]

DEAD_KEYWORDS = [
    'proxy/network error', 'error', 'timed out', 'connection failed'
]

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

async def get_bin_info(session, cc):
    try:
        bin6 = cc[:6]
        async with session.get(f"https://bins.antipublic.cc/bins/{bin6}", timeout=5) as res:
            if res.status == 200:
                data = await res.json()
                return (
                    data.get('brand', 'UNKNOWN'),
                    data.get('bank', 'UNKNOWN'),
                    data.get('country_name', 'UNKNOWN'),
                    data.get('level', 'N/A'),
                    data.get('type', 'N/A'),
                    data.get('country_flag', '')
                )
    except:
        pass
    return "UNKNOWN", "UNKNOWN", "UNKNOWN", "N/A", "N/A", ""

def classify_result(success, message):
    msg = message.lower()
    if 'insufficient_funds' in msg: return 'approved'
    if any(k in msg for k in ['approved', 'success', 'cvv', 'cvc', 'zip', 'incorrect_zip', 'invalid_cvv', 'invalid_cvc']): return 'approved'
    if success: return 'declined'
    return 'error'

def fmt_price(price, currency):
    try:
        if not price or price == '0': return "Free"
        return f"${float(price):.2f} {currency}"
    except:
        return f"${price} {currency}"

def fmt_info(brand, type_cc, level):
    if level and level != 'N/A':
        return f"{brand} - {type_cc.upper()} - {level.upper()}"
    return f"{brand} - {type_cc.upper()}"

async def run_with_retry(parts, proxy_str=None, max_retries=2):
    last_success, last_msg, last_gate, last_price, last_cur = False, 'ERROR', 'Stripe Charge', '1.00', 'USD'
    for attempt in range(max_retries):
        try:
            success, message, gateway, price, currency = await process_card(
                parts['cc'], parts['mes'], parts['ano'], parts['cvv'], "stripe", None, proxy_str
            )
            category = classify_result(success, message)
            if category != 'error':
                return success, message, gateway, price, currency, category
            if attempt < max_retries - 1: await asyncio.sleep(1)
        except Exception as e:
            last_msg = f"Error: {str(e)}"
            if attempt < max_retries - 1: await asyncio.sleep(1)
            else: break
    return last_success, last_msg, last_gate, last_price, last_cur, 'error'

def run_async_task(chat_id, cc_string, msg_to_edit=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def process_task():
        try:
            parts = parse_cc_string(cc_string)
        except ValueError as e:
            if msg_to_edit: bot.edit_message_text(f"❌ <b>Format Error:</b> {e}", chat_id, msg_to_edit)
            return

        async with aiohttp.ClientSession() as session:
            success, message, gateway, price, currency, category = await run_with_retry(parts)

            clean = extract_clean_response(message)
            brand, bank, country, level, type_cc, flag = await get_bin_info(session, parts['cc'])
            price_fmt = fmt_price(price, currency)
            info_str = fmt_info(brand, type_cc, level)

            status_map = {
                'approved': "🔵 <b>𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅</b>",
                'declined': "🔴 <b>𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝</b>",
                'error': "🟠 <b>𝐄𝐫𝐫𝐨𝐫</b>"
            }
            status_disp = status_map.get(category, "🟠 <b>𝐄𝐫𝐫𝐨𝐫</b>")

            final_text = (
                f"💳 𝐂𝐚𝐫𝐝 -» <code>{cc_string}</code>\n"
                f"📊 𝙎𝙩𝙖𝙩𝙪𝙨 -» {status_disp}\n"
                f"💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» <b>{clean}</b>\n"
                f"🛒 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -» <b>Stripe Charge</b>\n"
                f"💲 𝐏𝐫𝐢𝐜𝐞 -» <b>{price_fmt}</b>\n"
                f"━━━━━━━━━━━━━\n"
                f"ℹ️ 𝙄𝙣𝙛𝙤 -» {info_str}\n"
                f"🏦 𝘽𝙖𝙣𝙠 -» {bank}\n"
                f"🌍 𝘾𝙤𝙪𝗻𝘁𝗿𝐲 -» {country} {flag}\n"
                f"━━━━━━━━━━━━━"
            )

            if msg_to_edit: bot.edit_message_text(final_text, chat_id, msg_to_edit)
            else: bot.send_message(chat_id, final_text)

    loop.run_until_complete(process_task())
    loop.close()

def process_mass(chat_id, cards):
    for cc in cards:
        msg = bot.send_message(chat_id, f"⏳ <b>Checking:</b> <code>{cc}</code>")
        Thread(target=run_async_task, args=(chat_id, cc, msg.message_id)).start()
        time.sleep(3) # Stripe အတွက် ၃ စက္ကန့်ခြားပေးခြင်း

@bot.message_handler(commands=['admin', 'panel'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "🚫 Admin သာလျှင် ဤလုပ်ဆောင်ချက်ကို အသုံးပြုနိုင်ပါသည်။")
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ Proxy အသစ်ထည့်ရန်", callback_data="add_proxy"))
    markup.add(InlineKeyboardButton("🗑 Proxy အားလုံးဖျက်ရန်", callback_data="clear_proxy"))
    markup.add(InlineKeyboardButton("📊 Proxy အရေအတွက်စစ်ရန်", callback_data="count_proxy"))
    
    bot.send_message(message.chat.id, "👨‍💻 <b>Admin Control Panel</b>\nအောက်ပါခလုတ်များကိုနှိပ်၍ Proxy များကို စီမံနိုင်ပါသည်။", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.from_user.id != ADMIN_ID:
        return
        
    if call.data == "add_proxy":
        msg = bot.send_message(call.message.chat.id, "✏️ <b>Proxy အသစ်များကို အောက်ပါအတိုင်း (တစ်ကြောင်းလျှင်တစ်ခု) ပေးပို့ပါ:</b>\n\n<code>ip:port:user:pass</code>")
        bot.register_next_step_handler(msg, process_add_proxy)
        
    elif call.data == "clear_proxy":
        open("proxies.txt", "w").close()
        bot.answer_callback_query(call.id, "✅ Proxy အားလုံး ဖျက်ပစ်လိုက်ပါပြီ။", show_alert=True)
        
    elif call.data == "count_proxy":
        try:
            with open("proxies.txt", "r") as f:
                proxies = [line for line in f if line.strip()]
            count = len(proxies)
        except:
            count = 0
        bot.answer_callback_query(call.id, f"📊 လက်ရှိ Proxy အရေအတွက်: {count} ခု", show_alert=True)

def process_add_proxy(message):
    if message.from_user.id != ADMIN_ID: return
    lines = message.text.strip().split('\n')
    
    with open("proxies.txt", "a", encoding="utf-8") as f:
        for p in lines:
            if p.strip():
                f.write(p.strip() + "\n")
                
    bot.reply_to(message, f"✅ Proxy အသစ် {len(lines)} ခု အောင်မြင်စွာ ထည့်သွင်းပြီးပါပြီ။")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "🚫 <b>ခွင့်ပြုချက်မရှိပါ။</b>")
        return
    bot.reply_to(message, "မင်္ဂလာပါ၊ Command များကို ကြည့်ရှုရန် /cmd ကိုနှိပ်ပါ။")

@bot.message_handler(commands=['cmd'])
def send_cmd(message):
    if not is_authorized(message.from_user.id):
        return
        
    text = (
        "<b>🔥 Stripe Checker Bot 🔥</b>\n\n"
        "<b>(၁) Single Check:</b>\n<code>/chk 5275150060415544|05|27|803</code>\n\n"
        "<b>(၂) Mass Check:</b>\n<code>/chk mass\n5275150060415544|05|27|803\n4031630597626141|02|29|970</code>\n"
    )
    if message.from_user.id == ADMIN_ID:
        text += "\n<b>Admin Commands:</b>\n<code>/panel</code> (Proxy စီမံရန်)\n<code>/add UserID</code>\n<code>/rm UserID</code>"
    bot.reply_to(message, text)

@bot.message_handler(commands=['add'])
def add_user(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_user = int(message.text.split()[1])
        AUTHORIZED_USERS.add(new_user)
        bot.reply_to(message, f"✅ User ID <code>{new_user}</code> အား အသုံးပြုခွင့် ပေးလိုက်ပါပြီ။")
    except:
        bot.reply_to(message, "❌ အသုံးပြုနည်း: <code>/add UserID</code>")

@bot.message_handler(commands=['rm'])
def remove_user(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        rm_user = int(message.text.split()[1])
        if rm_user == ADMIN_ID:
            bot.reply_to(message, "❌ Admin ကို ဖျက်၍မရပါ။")
            return
        AUTHORIZED_USERS.discard(rm_user)
        bot.reply_to(message, f"🚫 User ID <code>{rm_user}</code> အား အသုံးပြုခွင့် ပိတ်လိုက်ပါပြီ။")
    except:
        bot.reply_to(message, "❌ အသုံးပြုနည်း: <code>/rm UserID</code>")

@bot.message_handler(commands=['chk'])
def check_command(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "🚫 <b>ခွင့်ပြုချက်မရှိပါ။</b>")
        return

    lines = message.text.strip().split('\n')
    first_line_args = lines[0].split()

    if len(first_line_args) > 1 and first_line_args[1].lower() == 'mass':
        cards = [line.strip() for line in lines[1:] if line.strip()]
        if not cards:
            bot.reply_to(message, "❌ ကတ်နံပါတ်များ မတွေ့ပါ။")
            return
        if len(cards) > 10:
            bot.reply_to(message, "⚠️ တစ်ကြိမ်လျှင် ကတ် (၁၀) ကတ်သာ အများဆုံး စစ်ဆေးနိုင်ပါသည်။")
            cards = cards[:10]
        bot.reply_to(message, f"⏳ <b>Mass Checking {len(cards)} Cards...</b>")
        Thread(target=process_mass, args=(message.chat.id, cards)).start()
    else:
        if len(first_line_args) == 2:
            cc_string = first_line_args[1]
            msg = bot.reply_to(message, f"⏳ <b>Checking Card...</b>")
            Thread(target=run_async_task, args=(message.chat.id, cc_string, msg.message_id)).start()
        else:
            bot.reply_to(message, "❌ <b>အသုံးပြုနည်း မှားယွင်းနေပါသည်။</b>")

@app.route('/')
def index():
    return "Stripe Bot is running perfectly!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    if not os.path.exists("proxies.txt"):
        open("proxies.txt", "w").close()
    
    try:
        with open("proxies.txt", "r") as f:
            if not f.read().strip():
                initial_proxies = [
                    "31.59.20.176:6754:klzmaipj:1ans3lrhk2lv",
                    "45.38.107.97:6014:klzmaipj:1ans3lrhk2lv",
                    "198.105.121.200:6462:klzmaipj:1ans3lrhk2lv",
                    "64.137.96.74:6641:klzmaipj:1ans3lrhk2lv",
                    "198.23.243.226:6361:klzmaipj:1ans3lrhk2lv",
                    "38.154.185.97:6370:klzmaipj:1ans3lrhk2lv",
                    "84.247.60.125:6095:klzmaipj:1ans3lrhk2lv",
                    "142.111.67.146:5611:klzmaipj:1ans3lrhk2lv",
                    "191.96.254.138:6185:klzmaipj:1ans3lrhk2lv",
                    "31.58.9.4:6077:klzmaipj:1ans3lrhk2lv"
                ]
                with open("proxies.txt", "w") as fp:
                    for p in initial_proxies:
                        fp.write(p + "\n")
    except:
        pass

    print("Stripe Bot Started...")
    bot.infinity_polling(timeout=20, long_polling_timeout=20)
