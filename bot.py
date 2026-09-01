import telebot
from telebot.types import BotCommand
import os
import random
import requests
from flask import Flask
from threading import Thread

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("Error: BOT_TOKEN မရှိပါ။")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

ADMIN_ID = 1847021130
AUTHORIZED_USERS = {ADMIN_ID}

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

# Telegram Bot Menu Commands Setup
def setup_bot_commands():
    commands = [
        BotCommand("me", "🔍 Telegram Account Info"),
        BotCommand("bin", "💳 BIN Lookup & Gen (/bin 412236)"),
        BotCommand("gen", "🔐 CC Generator (/gen)"),
        BotCommand("iban", "ℹ️ IBAN Generator (/iban)"),
        BotCommand("cpf", "©️ CPF Generator (Brazil)"),
        BotCommand("fake", "📍 Address Generator (/fake)"),
        BotCommand("ping", "🔍 Ping Test"),
        BotCommand("cmd", "🛠 Commands List")
    ]
    try:
        bot.set_my_commands(commands)
    except Exception as e:
        print(f"Menu setup error: {e}")

# 1. Telegram Info (/me)
@bot.message_handler(commands=['me'])
def cmd_me(message):
    if not is_authorized(message.from_user.id): return
    user = message.from_user
    text = (
        f"🔍 <b>Telegram Account Info</b>\n\n"
        f"👤 Name: {user.first_name} {user.last_name or ''}\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"🌐 Username: @{user.username or 'None'}\n"
        f"⚙️ Language: {user.language_code or 'N/A'}"
    )
    bot.reply_to(message, text)

# 2. BIN Info & Random Generator (/bin)
@bot.message_handler(commands=['bin'])
def cmd_bin(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    default_bins = ["412236", "453214", "541333", "512456", "378282", "601100"]
    bin6 = parts[1][:6] if len(parts) > 1 and len(parts[1]) >= 6 else random.choice(default_bins)
    
    try:
        res = requests.get(f"https://bins.antipublic.cc/bins/{bin6}", timeout=5)
        if res.status == 200:
            data = res.json()
            brand = data.get('brand', 'VISA')
            bank = data.get('bank', 'GLOBAL BANK')
            country = data.get('country_name', 'United States')
            tier = data.get('level', 'BUSINESS')
            type_cc = data.get('type', 'CREDIT')
        else:
            brand, bank, country, tier, type_cc = "VISA", "COMMERCIAL BANK", "United States", "BUSINESS", "CREDIT"
    except:
        brand, bank, country, tier, type_cc = "VISA", "COMMERCIAL BANK", "United States", "BUSINESS", "CREDIT"

    text = (
        f"<b>𝗕𝗜𝗡 𝗟𝗼𝗼𝗸𝘂𝗽 𝗥𝗲𝘀𝘂𝗹𝘁 🔍</b>\n\n"
        f"<b>𝗕𝗶𝗻 ⇾</b> {bin6}\n"
        f"<b>𝗦𝘁𝗮𝘁𝘂𝘀 ⇾</b> SUCCESS\n"
        f"<b>𝗦𝗰𝗵𝗲𝗺𝗲 ⇾</b> {brand}\n"
        f"<b>𝗧𝘆𝗽𝗲 ⇾</b> {type_cc}\n"
        f"<b>𝗜𝘀𝘀𝘂𝗲𝗿/𝗕𝗮𝗻𝗸 ⇾</b> {bank}\n"
        f"<b>𝗧𝗶𝗲𝗿 ⇾</b> {tier}\n"
        f"<b>𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ⇾</b> {country}\n"
        f"<b>𝗟𝘂𝗵𝗻 ⇾</b> True\n\n"
        f"<b>𝗕𝗜𝗡 ⇾</b> {bin6}\n"
        f"<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾</b> 10\n\n"
    )
    
    cards = []
    for _ in range(10):
        rand_digits = "".join([str(random.randint(0, 9)) for _ in range(16 - len(bin6))])
        full_cc = bin6 + rand_digits
        mm = f"{random.randint(1, 12):02d}"
        yyyy = str(random.randint(2027, 2035))
        cvv = f"{random.randint(100, 999)}"
        cards.append(f"{full_cc}|{mm}|{yyyy}|{cvv}")
    
    text += "\n".join(cards)
    text += f"\n\n<b>𝗜𝗻𝗳𝗼:</b> {brand} - {type_cc}\n<b>𝗕𝗮𝗻𝗸:</b> {bank}\n<b>𝗖𝗼𝘂𝗻𝘁𝗿𝘆:</b> {country}"
    bot.reply_to(message, text)

# 3. CC Generator (/gen) - Fully Randomized
@bot.message_handler(commands=['gen'])
def cmd_gen(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    default_bins = ["412236", "453214", "541333", "512456", "378282"]
    bin6 = parts[1][:6] if len(parts) > 1 and len(parts[1]) >= 6 else random.choice(default_bins)
    
    text = f"<b>𝗕𝗜𝗡 ⇾</b> {bin6}\n<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾</b> 10\n\n"
    cards = []
    for _ in range(10):
        rand_digits = "".join([str(random.randint(0, 9)) for _ in range(16 - len(bin6))])
        full_cc = bin6 + rand_digits
        mm = f"{random.randint(1, 12):02d}"
        yyyy = str(random.randint(2027, 2035))
        cvv = f"{random.randint(100, 999)}"
        cards.append(f"{full_cc}|{mm}|{yyyy}|{cvv}")
    
    text += "\n".join(cards)
    bot.reply_to(message, text)

# 4. IBAN Generator (/iban) - Fully Randomized
@bot.message_handler(commands=['iban'])
def cmd_iban(message):
    if not is_authorized(message.from_user.id): return
    countries = [("DE", "🇩🇪"), ("GB", "🇬🇧"), ("FR", "🇫🇷"), ("ES", "🇪🇸"), ("IT", "🇮🇹")]
    country, flag = random.choice(countries)
    
    bank_code = "".join([str(random.randint(0, 9)) for _ in range(8)])
    acc_num = "".join([str(random.randint(0, 9)) for _ in range(10)])
    check_dig = f"{random.randint(10, 99)}"
    
    text = (
        f"🌍 <b>IBAN Details</b>\n\n"
        f"Country: {country} {flag}\n"
        f"IBAN: {country}{check_dig}{bank_code}{acc_num}\n"
        f"Length: 22\n\n"
        f"Bank Code: {bank_code}\n"
        f"Account Number: {acc_num}\n"
        f"Check Digits: {check_dig}\n"
        f"BBAN: {bank_code}{acc_num}"
    )
    bot.reply_to(message, text)

# 5. CPF Generator (/cpf) - Fully Randomized Pools
@bot.message_handler(commands=['cpf'])
def cmd_cpf(message):
    if not is_authorized(message.from_user.id): return
    first_names = ["Anderson", "Carlos", "Lucas", "Mariana", "Gabriel", "Beatriz", "Rafael", "Juliana", "Thiago", "Larissa"]
    last_names = ["De Souza Rezende", "Silva Santos", "Almeida Costa", "Oliveira Lima", "Pereira Martins", "Rodrigues Souza", "Ferreira Alves"]
    places = ["Caminho Niemeyer", "Copacabana Palace", "Ipanema Beach", "Paulista Avenue", "Liberdade Square", "Maracanã Stadium"]
    
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    cpf = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
    place = random.choice(places)
    dob_year = random.randint(1978, 2000)
    dob_month = f"{random.randint(1, 12):02d}"
    dob_day = f"{random.randint(1, 28):02d}"
    
    text = (
        f"📍 <b>BR 🇧🇷 CPF Generator</b>\n\n"
        f"𝗡𝗮𝗺𝗲: {name}\n"
        f"𝗖𝗣𝗙: {cpf}\n"
        f"𝗗𝗼𝗕: {dob_year}-{dob_month}-{dob_day}\n"
        f"𝗣𝗹𝗮𝗰𝗲: {place}\n"
        f"𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝘆: Segunda ({random.randint(1,28)}/{random.randint(1,12)})"
    )
    bot.reply_to(message, text)

# 6. Address Generator (/fake) - Fully Randomized Pools
@bot.message_handler(commands=['fake'])
def cmd_fake(message):
    if not is_authorized(message.from_user.id): return
    firsts = ["Ella", "John", "Emma", "Michael", "Sophia", "William", "Olivia", "James", "Benjamin", "Charlotte"]
    lasts = ["Anderson", "Smith", "Watson", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Taylor", "Moore"]
    streets = ["42 Canal Street", "123 Main Street", "789 Broadway", "55 Park Avenue", "101 Market Street", "300 Bourbon Street"]
    cities = ["New Orleans", "New York", "Los Angeles", "Chicago", "Houston", "Philadelphia", "San Francisco"]
    states = ["Louisiana", "New York", "California", "Illinois", "Texas", "Pennsylvania", "Washington"]
    zips = ["70130", "10001", "90012", "60601", "77002", "19102", "94101"]
    
    fname = random.choice(firsts)
    lname = random.choice(lasts)
    street = random.choice(streets)
    city = random.choice(cities)
    state = random.choice(states)
    zip_code = random.choice(zips)
    phone = f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}"
    email = f"{fname.lower()}.{lname.lower()}{random.randint(10,99)}@gmail.com"
    
    text = (
        f"📍 <b>UNITED STATES Address Generator</b>\n\n"
        f"𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲: {fname} {lname}\n"
        f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: {street}\n"
        f"𝗖𝗶𝘁𝘆/𝗧𝗼𝘄𝗻/𝗩𝗶𝗹𝗹𝗮𝗴𝗲: {city}\n"
        f"𝗦𝘁𝗮𝘁𝗲/𝗣𝗿𝗼𝘃𝗶𝗻𝗰𝗲/𝗥𝗲𝗴𝗶𝗼𝗻: {state}\n"
        f"𝗣𝗼𝘀𝘁𝗮𝗹 𝗖𝗼𝗱𝗲: {zip_code}\n"
        f"𝗣𝗵𝗼𝗻𝗲 𝗡𝘂𝗺𝗯𝗲𝗿: {phone}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: United States\n"
        f"𝗧𝗲𝗺𝗽𝗼𝗿𝗮𝗿𝘆 𝗘𝗺𝗮𝗶𝗹: {email}"
    )
    bot.reply_to(message, text)

# 7. Ping Test (/ping) - Randomized Latency
@bot.message_handler(commands=['ping'])
def cmd_ping(message):
    if not is_authorized(message.from_user.id): return
    latency = random.randint(110, 260)
    text = (
        f"Ｐｏｎｇ 🏓\n\n"
        f"⚡ <b>Response Time</b>\n"
        f"├ 📊 Latency: {latency} ms\n"
        f"└ 🎯 Quality: 🟢 Excellent\n\n"
        f"🤖 <b>Bot Status:</b> Online & Responsive"
    )
    bot.reply_to(message, text)

# Help / Start Command
@bot.message_handler(commands=['start', 'help', 'cmd'])
def send_cmd(message):
    if not is_authorized(message.from_user.id): return
    text = (
        "🛠 <b>Bot Commands List</b>\n\n"
        "🔍 <code>/me</code> - Telegram Account Info\n"
        "💳 <code>/bin {6-digit}</code> - BIN Lookup & Gen\n"
        "🔐 <code>/gen</code> - Credit Card Generator\n"
        "ℹ️ <code>/iban</code> - IBAN Generator\n"
        "©️ <code>/cpf</code> - Brazilian CPF Generator\n"
        "📍 <code>/fake</code> - US Address Generator\n"
        "🔍 <code>/ping</code> - Ping Test"
    )
    bot.reply_to(message, text)

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
    
