import telebot
from telebot.types import BotCommand
import os
import random
import requests
from flask import Flask
from threading import Thread

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("Error: BOT_TOKEN ကို Render Environment တွင် မတွေ့ပါ။")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

ADMIN_ID = 1847021130
AUTHORIZED_USERS = {ADMIN_ID}

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

# Telegram Bot Menu Commands Setup (မီနူးဘားတွင် ခလုတ်များပေါ်စေရန်)
def setup_bot_commands():
    commands = [
        BotCommand("me", "🔍 Telegram Account Info"),
        BotCommand("bin", "💳 BIN Info (/bin 412236)"),
        BotCommand("gen", "🔐 CC Generator (/gen 412236)"),
        BotCommand("iban", "ℹ️ IBAN Generator (/iban US)"),
        BotCommand("cpf", "©️ CPF Generator"),
        BotCommand("fake", "📍 Address Generator (/fake US)"),
        BotCommand("ping", "🔍 Ping Test"),
        BotCommand("cmd", "🛠 Commands List & Help")
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

# 2. BIN Info (/bin)
@bot.message_handler(commands=['bin'])
def cmd_bin(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    if len(parts) != 2 or len(parts[1]) < 6:
        bot.reply_to(message, "❌ အသုံးပြုနည်း မှားယွင်းနေပါသည်။ ဥပမာ - <code>/bin 412236</code>")
        return
    
    bin6 = parts[1][:6]
    try:
        res = requests.get(f"https://bins.antipublic.cc/bins/{bin6}", timeout=5)
        if res.status == 200:
            data = res.json()
            text = (
                f"💳 <b>BIN Info:</b> <code>{bin6}</code>\n"
                f"🏦 Brand: {data.get('brand', 'UNKNOWN')}\n"
                f"🏛 Bank: {data.get('bank', 'UNKNOWN')}\n"
                f"🌍 Country: {data.get('country_name', 'UNKNOWN')} {data.get('country_flag', '')}\n"
                f"📊 Type: {data.get('type', 'N/A')}\n"
                f"💎 Level: {data.get('level', 'N/A')}"
            )
            bot.reply_to(message, text)
        else:
            bot.reply_to(message, "❌ ဤ BIN အချက်အလက်ကို ရှာမတွေ့ပါ။")
    except:
        bot.reply_to(message, "❌ Network Error ဖြစ်ပွားပါသည်။")

# 3. Smart CC Generator (/gen)
@bot.message_handler(commands=['gen'])
def cmd_gen(message):
    if not is_authorized(message.from_user.id): return
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "❌ အသုံးပြုနည်း: <code>/gen 412236</code> (သို့မဟုတ်) <code>/gen 412236xxxx|xx|2028|xxx</code>")
            return
        
        pattern = args[1].strip()
        cc_parts = pattern.split('|')
        
        template_cc = cc_parts[0]
        mm_template = cc_parts[1] if len(cc_parts) > 1 and cc_parts[1].strip() else "xx"
        yyyy_template = cc_parts[2] if len(cc_parts) > 2 and cc_parts[2].strip() else "2028"
        cvv_template = cc_parts[3] if len(cc_parts) > 3 and cc_parts[3].strip() else "xxx"
        
        cards_output = []
        for _ in range(10):
            curr_cc = "".join([str(random.randint(0, 9)) if char.lower() == 'x' else char for char in template_cc])
            if len(curr_cc) < 16:
                curr_cc += "".join([str(random.randint(0, 9)) for _ in range(16 - len(curr_cc))])
                
            curr_mm = f"{random.randint(1, 12):02d}" if 'x' in mm_template.lower() or mm_template == 'xx' else mm_template
            curr_yyyy = str(random.randint(2027, 2031)) if 'x' in yyyy_template.lower() or '20' not in yyyy_template else yyyy_template
            curr_cvv = "".join([str(random.randint(0, 9)) for _ in range(3)]) if 'x' in cvv_template.lower() or len(cvv_template) < 3 else cvv_template
            
            cards_output.append(f"<code>{curr_cc}|{curr_mm}|{curr_yyyy}|{curr_cvv}</code>")
            
        bot.reply_to(message, "🔐 <b>Generated Cards (10):</b>\n\n" + "\n".join(cards_output))
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# 4. IBAN Generator (/iban)
@bot.message_handler(commands=['iban'])
def cmd_iban(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    country = parts[1].upper() if len(parts) > 1 else "DE"
    rand_digits = "".join([str(random.randint(0, 9)) for _ in range(18)])
    fake_iban = f"{country}{random.randint(10,99)}{rand_digits}"
    bot.reply_to(message, f"ℹ️ <b>Generated IBAN ({country}):</b>\n<code>{fake_iban}</code>")

# 5. CPF Generator (/cpf)
@bot.message_handler(commands=['cpf'])
def cmd_cpf(message):
    if not is_authorized(message.from_user.id): return
    cpf = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
    bot.reply_to(message, f"©️ <b>Generated CPF:</b>\n<code>{cpf}</code>")

# 6. Advanced Fake Address Generator (/fake)
@bot.message_handler(commands=['fake'])
def cmd_fake(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    country = parts[1].upper() if len(parts) > 1 else "US"
    
    addresses = {
        "US": ("123 Main St", "New York", "NY", "10001", "+1 212-555-0198"),
        "UK": ("45 Baker Street", "London", "Greater London", "W1U 8ED", "+44 20 7946 0918"),
        "CA": ("789 Yonge St", "Toronto", "Ontario", "M4W 2G8", "+1 416-555-0143"),
        "DE": ("Hauptstraße 42", "Berlin", "Berlin", "10115", "+49 30 123456"),
        "FR": ("15 Rue de la Paix", "Paris", "Île-de-France", "75001", "+33 1 23 45 67 89")
    }
    
    addr = addresses.get(country, addresses["US"])
    text = (
        f"📍 <b>Fake Address ({country}):</b>\n\n"
        f"🏢 Street: <code>{addr[0]}</code>\n"
        f"🏙 City: <code>{addr[1]}</code>\n"
        f"📮 State/Region: <code>{addr[2]}</code>\n"
        f"📮 Zip/Postal: <code>{addr[3]}</code>\n"
        f"📞 Phone: <code>{addr[4]}</code>"
    )
    bot.reply_to(message, text)

# 7. Ping Test (/ping)
@bot.message_handler(commands=['ping'])
def cmd_ping(message):
    if not is_authorized(message.from_user.id): return
    bot.reply_to(message, "🏓 <b>Pong!</b> Server is active and running smoothly.")

# Help / Start Command with Country Codes list
@bot.message_handler(commands=['start', 'help', 'cmd'])
def send_cmd(message):
    if not is_authorized(message.from_user.id): return
    text = (
        "🛠 <b>Bot Commands List</b>\n\n"
        "🔍 <b>Telegram Info:</b> <code>/me</code>\n"
        "💳 <b>BIN Info:</b> <code>/bin {6-digit}</code>\n"
        "🔐 <b>CC Generator:</b> <code>/gen 412236</code>\n"
        "ℹ️ <b>IBAN Generator:</b> <code>/iban {country_code}</code>\n"
        "©️ <b>CPF Generator:</b> <code>/cpf</code>\n"
        "📍 <b>Address Generator:</b> <code>/fake {country_code}</code>\n"
        "🔍 <b>Ping Test:</b> <code>/ping</code>\n\n"
        "🌐 <b>Available Country Codes:</b>\n"
        "• <b>US</b> - United States\n"
        "• <b>UK</b> - United Kingdom\n"
        "• <b>CA</b> - Canada\n"
        "• <b>DE</b> - Germany\n"
        "• <b>FR</b> - France"
    )
    bot.reply_to(message, text)

# Flask server for Render port binding (Keepalive)
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
    
