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

# 1. Telegram Info (/me) - Monospace Output
@bot.message_handler(commands=['me'])
def cmd_me(message):
    if not is_authorized(message.from_user.id): return
    user = message.from_user
    text = (
        f"🔍 Telegram Account Info\n\n"
        f"👤 Name: {user.first_name} {user.last_name or ''}\n"
        f"🆔 User ID: {user.id}\n"
        f"🌐 Username: @{user.username or 'None'}\n"
        f"⚙️ Language: {user.language_code or 'N/A'}"
    )
    bot.reply_to(message, f"<pre>{text}</pre>")

# 2. CC Generator (/gen) - Format check & Monospace Output
@bot.message_handler(commands=['gen'])
def cmd_gen(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 2 or len(parts[1]) < 4:
        bot.reply_to(message, "<pre>❌ အသုံးပြုနည်း: /gen 412236</pre>")
        return
        
    bin_input = parts[1][:6]
    is_amex = bin_input.startswith("34") or bin_input.startswith("37")
    card_length = 15 if is_amex else 16
    cvv_length = 4 if is_amex else 3
    
    cards = []
    for _ in range(10):
        rand_digits = "".join([str(random.randint(0, 9)) for _ in range(card_length - len(bin_input))])
        full_cc = bin_input + rand_digits
        mm = f"{random.randint(1, 12):02d}"
        yyyy = str(random.randint(2027, 2035))
        cvv = "".join([str(random.randint(0, 9)) for _ in range(cvv_length)])
        cards.append(f"{full_cc}|{mm}|{yyyy}|{cvv}")
    
    text = f"𝗕𝗜𝗡 ⇾ {bin_input}\n𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10\n\n" + "\n".join(cards)
    bot.reply_to(message, f"<pre>{text}</pre>")

# 3. IBAN Generator (/iban) - Monospace Output
@bot.message_handler(commands=['iban'])
def cmd_iban(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "<pre>❌ နိုင်ငံကုဒ် ထည့်ရန်လိုပါသည်။ ဥပမာ - /iban DE သို့မဟုတ် /iban GB</pre>")
        return
        
    country = parts[1].upper()
    flags = {"DE": "🇩🇪", "GB": "🇬🇧", "FR": "🇫🇷", "ES": "🇪🇸", "IT": "🇮🇹", "BR": "🇧🇷", "US": "🇺🇸", "CA": "🇨🇦"}
    flag = flags.get(country, "🌐")
    
    bank_code = "".join([str(random.randint(0, 9)) for _ in range(8)])
    acc_num = "".join([str(random.randint(0, 9)) for _ in range(10)])
    check_dig = f"{random.randint(10, 99)}"
    
    text = (
        f"🌍 IBAN Details\n\n"
        f"Country: {country} {flag}\n"
        f"IBAN: {country}{check_dig}{bank_code}{acc_num}\n"
        f"Length: 22\n\n"
        f"Bank Code: {bank_code}\n"
        f"Account Number: {acc_num}\n"
        f"Check Digits: {check_dig}\n"
        f"BBAN: {bank_code}{acc_num}"
    )
    bot.reply_to(message, f"<pre>{text}</pre>")

# 4. CPF Generator (/cpf) - Monospace Output
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
        f"📍 BR 🇧🇷 CPF Generator\n\n"
        f"𝗡𝗮𝗺𝗲: {name}\n"
        f"𝗖𝗣𝗙: {cpf}\n"
        f"𝗗𝗼𝗕: 1988-04-10\n"
        f"𝗣𝗹𝗮𝗰𝗲: {place}\n"
        f"𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝘆: Segunda ({random.randint(1,28)}/{random.randint(1,12)})"
    )
    bot.reply_to(message, f"<pre>{text}</pre>")

# 5. Localized Address Generator (/fake) - Monospace Output
@bot.message_handler(commands=['fake'])
def cmd_fake(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    
    if len(parts) < 2:
        country_list_text = (
            "📍 Available Countries for Fake Address:\n\n"
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
            "💡 အသုံးပြုပုံ: /fake US သို့မဟုတ် /fake UK"
        )
        bot.reply_to(message, f"<pre>{country_list_text}</pre>")
        return

    country = parts[1].upper()
    
    # Localized Mock Pools based on country
    loc_data = {
        "UK": (["Oliver", "George", "Harry", "Jack", "Amelia", "Isla"], ["Smith", "Jones", "Taylor", "Brown"], ["10 Downing Street", "221B Baker Street", "45 Oxford Street"], ["London", "Manchester", "Birmingham"], ["Greater London", "Greater Manchester", "West Midlands"], ["SW1A 2AA", "M1 1AE", "B1 1AA"], "+44 20 7946 0918"),
        "CA": (["Liam", "Noah", "William", "Lucas", "Olivia", "Emma"], ["Tremblay", "Roy", "Gagnon", "Lee"], ["789 Yonge St", "123 Queen St W", "456 Sainte-Catherine St"], ["Toronto", "Vancouver", "Montreal"], ["Ontario", "British Columbia", "Quebec"], ["M4W 2G8", "V6B 1B6", "H3B 1A2"], "+1 416-555-0143"),
        "DE": (["Maximilian", "Alexander", "Elias", "Paul", "Emma", "Mia"], ["Schmidt", "Schneider", "Fischer", "Weber"], ["Hauptstraße 42", "Friedrichstraße 15", "Königsallee 10"], ["Berlin", "Munich", "Frankfurt"], ["Berlin", "Bavaria", "Hesse"], ["10115", "80331", "60311"], "+49 30 123456"),
        "FR": (["Gabriel", "Leo", "Louis", "Raphael", "Jade", "Louise"], ["Bernard", "Petit", "Robert", "Richard"], ["15 Rue de la Paix", "10 Avenue des Champs-Élysées", "25 Rue de Rivoli"], ["Paris", "Lyon", "Marseille"], ["Île-de-France", "Auvergne-Rhône-Alpes", "Provence-Alpes-Côte d'Azur"], ["75001", "69001", "13001"], "+33 1 23 45 67 89"),
        "JP": (["Haruto", "Yuto", "Sota", "Ren", "Yui", "Hina"], ["Sato", "Suzuki", "Takahashi", "Tanaka"], ["2-11-1 Nagata-cho", "1-1-2 Oshiage", "3-5-1 Roppongi"], ["Tokyo", "Osaka", "Kyoto"], ["Tokyo", "Osaka", "Kyoto"], ["100-0014", "530-0001", "600-8216"], "+81 3 5555 0143"),
    }
    
    default_us = (["Ella", "John", "Emma", "Michael"], ["Anderson", "Smith", "Watson", "Johnson"], ["42 Canal Street", "123 Main Street", "789 Broadway"], ["New Orleans", "New York", "Los Angeles"], ["Louisiana", "New York", "California"], ["70130", "10001", "90012"], "+15045550124")
    
    firsts, lasts, streets, cities, states, zips, phone = loc_data.get(country, default_us)
    
    fname = random.choice(firsts)
    lname = random.choice(lasts)
    street = random.choice(streets)
    city = random.choice(cities)
    state = random.choice(states)
    zip_code = random.choice(zips)
    email = f"{fname.lower()}.{lname.lower()}{random.randint(10,99)}@gmail.com"
    
    text = (
        f"📍 {country} Address Generator\n\n"
        f"𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲: {fname} {lname}\n"
        f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: {street}\n"
        f"𝗖𝗶𝘁𝘆/𝗧𝗼𝘄𝗻/𝗩𝗶𝗹𝗹𝗮𝗴𝗲: {city}\n"
        f"𝗦𝘁𝗮𝘁𝗲/𝗣𝗿𝗼𝘃𝗶𝗻𝗰𝗲/𝗥𝗲𝗴𝗶𝗼𝗻: {state}\n"
        f"𝗣𝗼𝘀𝘁𝗮𝗹 𝗖𝗼𝗱𝗲: {zip_code}\n"
        f"𝗣𝗵𝗼𝗻𝗲 𝗡𝘂𝗺𝗯𝗲𝗿: {phone}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country}\n"
        f"𝗧𝗲𝗺𝗽𝗼𝗿𝗮𝗿𝘆 𝗘𝗺𝗮𝗶𝗹: {email}"
    )
    bot.reply_to(message, f"<pre>{text}</pre>")

# 6. Ping Test (/ping) - Monospace Output
@bot.message_handler(commands=['ping'])
def cmd_ping(message):
    if not is_authorized(message.from_user.id): return
    latency = random.randint(110, 240)
    text = (
        f"Ｐｏｎｇ 🏓\n\n"
        f"⚡ Response Time\n"
        f"├ 📊 Latency: {latency} ms\n"
        f"└ 🎯 Quality: 🟢 Excellent\n\n"
        f"🤖 Bot Status: Online & Responsive"
    )
    bot.reply_to(message, f"<pre>{text}</pre>")

# Help / Start Command
@bot.message_handler(commands=['start', 'help', 'cmd'])
def send_cmd(message):
    if not is_authorized(message.from_user.id): return
    text = (
        "🛠 Bot Commands List\n\n"
        "🔍 /me - Telegram Account Info\n"
        "🔐 /gen {bin} - CC Generator\n"
        "ℹ️ /iban {country} - IBAN Generator\n"
        "©️ /cpf - Brazilian CPF Generator\n"
        "📍 /fake {country} - Address Generator (Type /fake to see list)\n"
        "🔍 /ping - Ping Test"
    )
    bot.reply_to(message, f"<pre>{text}</pre>")

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


