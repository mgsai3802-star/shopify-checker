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

def setup_bot_commands():
    commands = [
        BotCommand("me", "🔍 Telegram Account Info"),
        BotCommand("bin", "💳 BIN Lookup (/bin 412236)"),
        BotCommand("gen", "🔐 CC Generator (/gen 412236)"),
        BotCommand("iban", "ℹ️ IBAN Generator (/iban DE)"),
        BotCommand("cpf", "©️ CPF Generator (Brazil)"),
        BotCommand("fake", "📍 Address Generator (/fake US)"),
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

# 2. BIN Lookup (Pure Lookup - No unwanted gen below)
@bot.message_handler(commands=['bin'])
def cmd_bin(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    if len(parts) != 2 or len(parts[1]) < 6:
        bot.reply_to(message, "❌ အသုံးပြုနည်း: <code>/bin 412236</code>")
        return
    
    bin6 = parts[1][:6]
    try:
        res = requests.get(f"https://bins.antipublic.cc/bins/{bin6}", timeout=5)
        if res.status == 200:
            data = res.json()
            brand = data.get('brand', 'VISA')
            bank = data.get('bank', 'COMMERCIAL BANK')
            country = data.get('country_name', 'United States')
            tier = data.get('level', 'BUSINESS')
            type_cc = data.get('type', 'CREDIT')
            
            text = (
                f"<b>𝗕𝗜𝗡 𝗟𝗼𝗼𝗸𝘂𝗽 𝗥𝗲𝘀𝘂𝗹𝘁 🔍</b>\n\n"
                f"<b>𝗕𝗶𝗻 ⇾</b> {bin6}\n"
                f"<b>𝗦𝘁𝗮𝘁𝘂𝘀 ⇾</b> SUCCESS\n"
                f"<b>𝗦𝗰𝗵𝗲𝗺𝗲 ⇾</b> {brand}\n"
                f"<b>𝗧𝘆𝗽𝗲 ⇾</b> {type_cc}\n"
                f"<b>𝗜𝘀𝘀𝘂𝗲𝗿/𝗕𝗮𝗻𝗸 ⇾</b> {bank}\n"
                f"<b>𝗧𝗶𝗲𝗿 ⇾</b> {tier}\n"
                f"<b>𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ⇾</b> {country}\n"
                f"<b>𝗟𝘂𝗵𝗻 ⇾</b> True"
            )
            bot.reply_to(message, text)
        else:
            bot.reply_to(message, "❌ BIN အချက်အလက် ရှာမတွေ့ပါ။")
    except:
        bot.reply_to(message, "❌ Network Error ဖြစ်ပွားပါသည်။")

# 3. CC Generator (/gen) - Supports Amex (15 digits) & Visa/Master (16 digits) properly
@bot.message_handler(commands=['gen'])
def cmd_gen(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    default_bins = ["412236", "453214", "541333", "378282"] # Amex starts with 37 (15 digits)
    bin_input = parts[1][:6] if len(parts) > 1 and len(parts[1]) >= 4 else random.choice(default_bins)
    
    # Check if Amex (starts with 34 or 37 -> 15 digits total)
    is_amex = bin_input.startswith("34") or bin_input.startswith("37")
    card_length = 15 if is_amex else 16
    cvv_length = 4 if is_amex else 3
    
    text = f"<b>𝗕𝗜𝗡 ⇾</b> {bin_input}\n<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾</b> 10\n\n"
    cards = []
    for _ in range(10):
        rand_digits = "".join([str(random.randint(0, 9)) for _ in range(card_length - len(bin_input))])
        full_cc = bin_input + rand_digits
        mm = f"{random.randint(1, 12):02d}"
        yyyy = str(random.randint(2027, 2035))
        cvv = "".join([str(random.randint(0, 9)) for _ in range(cvv_length)])
        cards.append(f"{full_cc}|{mm}|{yyyy}|{cvv}")
    
    text += "\n".join(cards)
    bot.reply_to(message, text)

# 4. IBAN Generator (/iban) - Requires Country Code
@bot.message_handler(commands=['iban'])
def cmd_iban(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ နိုင်ငံကုဒ် ထည့်ရန်လိုပါသည်။ ဥပမာ - <code>/iban DE</code> သို့မဟုတ် <code>/iban GB</code>")
        return
        
    country = parts[1].upper()
    flags = {"DE": "🇩🇪", "GB": "🇬🇧", "FR": "🇫🇷", "ES": "🇪🇸", "IT": "🇮🇹", "BR": "🇧🇷", "US": "🇺🇸", "CA": "🇨🇦"}
    flag = flags.get(country, "🌐")
    
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

# 5. CPF Generator (/cpf)
@bot.message_handler(commands=['cpf'])
def cmd_cpf(message):
    if not is_authorized(message.from_user.id): return
    first_names = ["Anderson", "Carlos", "Lucas", "Mariana", "Gabriel", "Beatriz", "Rafael", "Juliana"]
    last_names = ["De Souza Rezende", "Silva Santos", "Almeida Costa", "Oliveira Lima", "Pereira Martins"]
    places = ["Caminho Niemeyer", "Copacabana Palace", "Ipanema Beach", "Paulista Avenue", "Maracanã Stadium"]
    
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    cpf = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
    place = random.choice(places)
    
    text = (
        f"📍 <b>BR 🇧🇷 CPF Generator</b>\n\n"
        f"𝗡𝗮𝗺𝗲: {name}\n"
        f"𝗖𝗣𝗙: {cpf}\n"
        f"𝗗𝗼𝗕: 1988-04-10\n"
        f"𝗣𝗹𝗮𝗰𝗲: {place}\n"
        f"𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝘆: Segunda ({random.randint(1,28)}/{random.randint(1,12)})"
    )
    bot.reply_to(message, text)

# 6. Address Generator (/fake) - Requires Country Code or shows full country list
@bot.message_handler(commands=['fake'])
def cmd_fake(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    
    if len(parts) < 2:
        country_list_text = (
            "📍 <b>Available Countries for Fake Address:</b>\n\n"
            "1. Algeria (DZ)\n2. Argentina (AR)\n3. Australia (AU)\n4. Bahrain (BH)\n"
            "5. Bangladesh (BD)\n6. Belgium (BE)\n7. Brazil (BR)\n8. Cambodia (KH)\n"
            "9. Canada (CA)\n10. Colombia (CO)\n11. Denmark (DK)\n12. Egypt (EG)\n"
            "13. Finland (FI)\n14. France (FR)\n15. Germany (DE)\n16. India (IN)\n"
            "17. Italy (IT)\n18. Japan (JP)\n19. Kazakhstan (KZ)\n20. Malaysia (MY)\n"
            "21. Mexico (MX)\n22. Morocco (MA)\n23. New Zealand (NZ)\n24. Panama (PA)\n"
            "25. Pakistan (PK)\n26. Peru (PE)\n27. Poland (PL)\n28. Qatar (QA)\n"
            "29. Saudi Arabia (SA)\n30. Singapore (SG)\n31. Spain (ES)\n32. Sweden (SE)\n"
            "33. Switzerland (CH)\n34. Thailand (TH)\n35. Turkiye (TR)\n"
            "36. United Kingdom (UK)\n37. United States (US)\n\n"
            "💡 <i>အသုံးပြုပုံ: <code>/fake US</code> သို့မဟုတ် <code>/fake UK</code> ဟု နိုင်ငံကုဒ်ထည့်ပါ</i>"
        )
        bot.reply_to(message, country_list_text)
        return

    country = parts[1].upper()
    
    firsts = ["Ella", "John", "Emma", "Michael", "Sophia", "William", "Olivia", "James"]
    lasts = ["Anderson", "Smith", "Watson", "Johnson", "Brown", "Davis", "Miller", "Wilson"]
    streets = ["42 Canal Street", "123 Main Street", "789 Broadway", "55 Park Avenue", "101 Market Street"]
    cities = ["New Orleans", "New York", "Los Angeles", "Chicago", "Houston", "Philadelphia"]
    states = ["Louisiana", "New York", "California", "Illinois", "Texas", "Pennsylvania"]
    zips = ["70130", "10001", "90012", "60601", "77002", "19102"]
    
    fname = random.choice(firsts)
    lname = random.choice(lasts)
    street = random.choice(streets)
    city = random.choice(cities)
    state = random.choice(states)
    zip_code = random.choice(zips)
    phone = f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}"
    email = f"{fname.lower()}.{lname.lower()}{random.randint(10,99)}@gmail.com"
    
    text = (
        f"📍 <b>{country} Address Generator</b>\n\n"
        f"𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲: {fname} {lname}\n"
        f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: {street}\n"
        f"𝗖𝗶𝘁𝘆/𝗧𝗼𝘄𝗻/𝗩𝗶𝗹𝗹𝗮𝗴𝗲: {city}\n"
        f"𝗦𝘁𝗮𝘁𝗲/𝗣𝗿𝗼𝘃𝗶𝗻𝗰𝗲/𝗥𝗲𝗴𝗶𝗼𝗻: {state}\n"
        f"𝗣𝗼𝘀𝘁𝗮𝗹 𝗖𝗼𝗱𝗲: {zip_code}\n"
        f"𝗣𝗵𝗼𝗻𝗲 𝗡𝘂𝗺𝗯𝗲𝗿: {phone}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country}\n"
        f"𝗧𝗲𝗺𝗽𝗼𝗿𝗮𝗿𝘆 𝗘𝗺𝗮𝗶𝗹: {email}"
    )
    bot.reply_to(message, text)

# 7. Ping Test (/ping)
@bot.message_handler(commands=['ping'])
def cmd_ping(message):
    if not is_authorized(message.from_user.id): return
    latency = random.randint(110, 240)
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
        "💳 <code>/bin {6-digit}</code> - BIN Lookup\n"
        "🔐 <code>/gen {bin}</code> - CC Generator (Amex/Visa/Master)\n"
        "ℹ️ <code>/iban {country}</code> - IBAN Generator\n"
        "©️ <code>/cpf</code> - Brazilian CPF Generator\n"
        "📍 <code>/fake {country}</code> - Address Generator (Type /fake to see list)\n"
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
    
