import telebot
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

# 3. CC Generator (/gen)
@bot.message_handler(commands=['gen'])
def cmd_gen(message):
    if not is_authorized(message.from_user.id): return
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "❌ အသုံးပြုနည်း: <code>/gen 412236xxxx|xx|2025|xxx</code>")
            return
        
        pattern = args[1]
        cc_parts = pattern.split('|')
        if len(cc_parts) != 4:
            bot.reply_to(message, "❌ ပုံစံမှားနေပါသည်။ ဥပမာ - <code>/gen 412236xxxx|xx|2025|xxx</code>")
            return
            
        template_cc, mm_template, yyyy_template, cvv_template = cc_parts
        cards_output = []
        
        for _ in range(10):
            curr_cc = "".join([str(random.randint(0, 9)) if char.lower() == 'x' else char for char in template_cc])
            curr_mm = f"{random.randint(1, 12):02d}" if 'x' in mm_template.lower() or mm_template == 'xx' else mm_template
            curr_yyyy = str(random.randint(2025, 2030)) if 'x' in yyyy_template.lower() or '20' not in yyyy_template else yyyy_template
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

# 6. Address Generator (/fake)
@bot.message_handler(commands=['fake'])
def cmd_fake(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    country = parts[1].upper() if len(parts) > 1 else "US"
    text = (
        f"📍 <b>Fake Address ({country}):</b>\n\n"
        f"🏢 Street: 123 Main St\n"
        f"🏙 City: New York\n"
        f"📮 State: NY\n"
        f"📮 Zip Code: 10001\n"
        f"📞 Phone: +1 2125550198"
    )
    bot.reply_to(message, text)

# 7. Ping Test (/ping)
@bot.message_handler(commands=['ping'])
def cmd_ping(message):
    if not is_authorized(message.from_user.id): return
    bot.reply_to(message, "🏓 <b>Pong!</b> Server is active and running smoothly.")

# Help / Start Command
@bot.message_handler(commands=['start', 'help', 'cmd'])
def send_cmd(message):
    if not is_authorized(message.from_user.id): return
    text = (
        "🛠 <b>Bot Commands List</b>\n\n"
        "🔍 <b>Telegram Info:</b> <code>/me</code>\n"
        "💳 <b>BIN Info:</b> <code>/bin {6-digit}</code>\n"
        "🔐 <b>CC Generator:</b> <code>/gen CARD|MM|YYYY|CVV</code>\n"
        "ℹ️ <b>IBAN Generator:</b> <code>/iban {country}</code>\n"
        "©️ <b>CPF Generator:</b> <code>/cpf</code>\n"
        "📍 <b>Address Generator:</b> <code>/fake {country}</code>\n"
        "🔍 <b>Ping Test:</b> <code>/ping</code>"
    )
    bot.reply_to(message, text)

# Flask server for Render port binding (Keepalive)
@app.route('/')
def index():
    return "Multi-tools Bot is running successfully!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    print("Multi-tools Telegram Bot Started...")
    bot.infinity_polling()


