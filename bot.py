import telebot
from telebot.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton
import os
import random
import requests
import re
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

# --- Main Keyboard Menu ---
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("🔐 Gen BIN"), KeyboardButton("👉 Fake Address"))
    markup.add(KeyboardButton("ℹ️ IBAN Gen"), KeyboardButton("©️ CPF Gen"))
    markup.add(KeyboardButton("👤 My Info"))
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
    menu_buttons = ["🔐 Gen BIN", "👉 Fake Address", "ℹ️ IBAN Gen", "©️ CPF Gen", "👤 My Info"]
    if text in menu_buttons or text.startswith('/'):
        handle_menu_buttons(message)
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
        "👉 /fake - Address Generator\n"
        "ℹ️ /iban - IBAN Generator\n"
        "©️ /cpf - CPF Generator\n"
        "👤 /me - My Info"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu())

@bot.message_handler(commands=['start'])
def cmd_start(message):
    add_user(message.from_user.id) 
    if is_banned(message.from_user.id): return
    bot.reply_to(message, "🛠 <b>Bot Main Menu</b>\nအောက်ပါ ခလုတ်များကို နှိပ်၍ အသုံးပြုပါ။ Genနှင့်Addressသည် Fommatမှန်က တန်းပို့နိုင်သည်။ (ဥပမာ-524554555|xx|xx|xxxနှင့် us/uk/de/etc....)", reply_markup=get_main_menu())

# --- Direct Functions for Info & CPF ---
def cmd_me(message):
    user = message.from_user
    text = (
        f"🔍 <b>Telegram Account Info</b>\n\n"
        f"👤 Name: <code>{user.first_name} {user.last_name or ''}</code>\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"🌐 Username: <code>@{user.username or 'None'}</code>\n"
        f"⚙️ Language: <code>{user.language_code or 'N/A'}</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu())

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
    bot.reply_to(message, text, reply_markup=get_main_menu())

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
    bot.reply_to(message, text, reply_markup=get_main_menu())

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
                bot.reply_to(message, text, reply_markup=get_main_menu())
                return
        except:
            pass 

    loc_database = {
        "dz": {"country": "Algeria 🇩🇿", "first": ["Amine", "Fatima", "Mohamed", "Amina"], "last": ["Benali", "Khelifi", "Brahimi", "Mansouri"], "streets": ["Rue Didouche Mourad", "Blvd Mohamed V"], "cities": ["Algiers", "Oran", "Constantine"], "states": ["Algiers", "Oran"], "zips": ["16000", "31000", "25000"], "phone": f"+213 55{random.randint(100000, 999999):06d}"},
        "ar": {"country": "Argentina 🇦🇷", "first": ["Mateo", "Sofia", "Lucas", "Valentina"], "last": ["Gomez", "Fernandez", "Lopez", "Diaz"], "streets": ["Av. Corrientes", "Calle Florida"], "cities": ["Buenos Aires", "Cordoba"], "states": ["Buenos Aires", "Cordoba"], "zips": ["C1043", "X5000"], "phone": f"+54 9 11 {random.randint(1000,9999)}-{random.randint(1000,9999)}"},
        "au": {"country": "Australia 🇦🇺", "first": ["Jack", "Charlotte", "Oliver"], "last": ["Smith", "Wilson", "Johnson"], "streets": ["Collins St", "George St"], "cities": ["Sydney", "Melbourne"], "states": ["NSW", "Victoria"], "zips": ["2000", "3000"], "phone": f"+61 4{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}"},
        "bh": {"country": "Bahrain 🇧🇭", "first": ["Ali", "Zainab", "Mohammed", "Fatima"], "last": ["Hassan", "Ahmed", "Al-Khalifa"], "streets": ["Road No 2803", "King Faisal Hwy"], "cities": ["Manama", "Riffa"], "states": ["Capital", "Southern"], "zips": ["328", "901"], "phone": f"+973 {random.choice([33,34,36,39])}{random.randint(100000, 999999):06d}"},
        "bd": {"country": "Bangladesh 🇧🇩", "first": ["Rahim", "Ayesha", "Tanvir", "Nusrat"], "last": ["Uddin", "Begum", "Ahmed"], "streets": ["Motijheel C/A", "Gulshan Ave"], "cities": ["Dhaka", "Chittagong"], "states": ["Dhaka", "Chittagong"], "zips": ["1000", "4000"], "phone": f"+880 17{random.randint(10000000, 99999999)}"},
        "be": {"country": "Belgium 🇧🇪", "first": ["Lucas", "Camille", "Arthur"], "last": ["Janssen", "Dubois", "Peeters"], "streets": ["Rue de la Loi", "Meir"], "cities": ["Brussels", "Antwerp"], "states": ["Brussels", "Flanders"], "zips": ["1000", "2000"], "phone": f"+32 4{random.randint(70,99)} {random.randint(100000,999999)}"},
        "br": {"country": "Brazil 🇧🇷", "first": ["Anderson", "Mariana", "Gabriel"], "last": ["Silva", "Santos", "Oliveira"], "streets": ["Av. Paulista", "Copacabana"], "cities": ["São Paulo", "Rio de Janeiro"], "states": ["SP", "RJ"], "zips": ["01310-100", "22041-001"], "phone": f"+55 11 9{random.randint(1000,9999)}-{random.randint(1000,9999)}"},
        "kh": {"country": "Cambodia 🇰🇭", "first": ["Sokha", "Vanna", "Dara", "Chan"], "last": ["Chan", "Seng", "Chea"], "streets": ["Preah Monivong Blvd", "Sihanouk Blvd"], "cities": ["Phnom Penh", "Siem Reap"], "states": ["Phnom Penh", "Siem Reap"], "zips": ["12000", "17000"], "phone": f"+855 {random.choice([10,12,69,93])} {random.randint(100, 999)} {random.randint(100, 999)}"},
        "ca": {"country": "Canada 🇨🇦", "first": ["Liam", "Olivia", "Noah"], "last": ["Tremblay", "Roy", "Gagnon"], "streets": ["Yonge St", "Queen St W"], "cities": ["Toronto", "Vancouver"], "states": ["Ontario", "British Columbia"], "zips": ["M4W 2G8", "V6B 1B6"], "phone": f"+1 416-{random.randint(200,999)}-{random.randint(1000,9999)}"},
        "co": {"country": "Colombia 🇨🇴", "first": ["Santiago", "Valeria", "Mateo"], "last": ["Rodriguez", "Lopez", "Garcia"], "streets": ["Cra. 7", "Calle 50"], "cities": ["Bogota", "Medellin"], "states": ["Cundinamarca", "Antioquia"], "zips": ["110311", "050001"], "phone": f"+57 3{random.randint(10,29)} {random.randint(1000000, 9999999)}"},
        "dk": {"country": "Denmark 🇩🇰", "first": ["Magnus", "Ida", "Oliver"], "last": ["Nielsen", "Jensen", "Hansen"], "streets": ["Strøget", "Vesterbrogade"], "cities": ["Copenhagen", "Aarhus"], "states": ["Capital Region", "Central Denmark"], "zips": ["1160", "8000"], "phone": f"+45 {random.randint(20,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}"},
        "eg": {"country": "Egypt 🇪🇬", "first": ["Ahmed", "Nour", "Mohamed", "Salma"], "last": ["Mohamed", "Ibrahim", "Hassan"], "streets": ["Tahrir Square", "Corniche El Nil"], "cities": ["Cairo", "Alexandria"], "states": ["Cairo", "Alexandria"], "zips": ["11511", "21500"], "phone": f"+20 10 {random.randint(1000,9999)} {random.randint(1000,9999)}"},
        "fi": {"country": "Finland 🇫🇮", "first": ["Eetu", "Aino", "Leo"], "last": ["Korhonen", "Virtanen", "Mäkinen"], "streets": ["Mannerheimintie", "Aleksanterinkatu"], "cities": ["Helsinki", "Espoo"], "states": ["Uusimaa", "Pirkanmaa"], "zips": ["00100", "02100"], "phone": f"+358 40 {random.randint(100,999)} {random.randint(1000,9999)}"},
        "fr": {"country": "France 🇫🇷", "first": ["Gabriel", "Jade", "Louis"], "last": ["Bernard", "Petit", "Robert"], "streets": ["Rue de la Paix", "Champs-Élysées"], "cities": ["Paris", "Lyon"], "states": ["Île-de-France", "Auvergne-Rhône-Alpes"], "zips": ["75001", "69001"], "phone": f"+33 6 {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}"},
        "de": {"country": "Germany 🇩🇪", "first": ["Maximilian", "Anna", "Alexander"], "last": ["Schmidt", "Weber", "Fischer"], "streets": ["Hauptstraße", "Friedrichstraße"], "cities": ["Berlin", "Munich"], "states": ["Berlin", "Bavaria"], "zips": ["10115", "80331"], "phone": f"+49 151 {random.randint(1000000,9999999)}"},
        "id": {"country": "Indonesia 🇮🇩", "first": ["Budi", "Siti", "Agus", "Ayu"], "last": ["Setiawan", "Lestari", "Santoso", "Saputra"], "streets": ["Jl. Sudirman", "Jl. Thamrin", "Jl. Gatot Subroto"], "cities": ["Jakarta", "Surabaya", "Bandung", "Medan"], "states": ["DKI Jakarta", "Jawa Timur", "Jawa Barat"], "zips": ["10110", "60271", "40111"], "phone": f"+62 8{random.choice([1,2,5,9])} {random.randint(1000,9999)} {random.randint(1000,9999)}"},
        "in": {"country": "India 🇮🇳", "first": ["Aarav", "Diya", "Vivaan"], "last": ["Sharma", "Patel", "Gupta"], "streets": ["MG Road", "Connaught Place"], "cities": ["Mumbai", "Delhi"], "states": ["Maharashtra", "Delhi"], "zips": ["400001", "110001"], "phone": f"+91 9{random.randint(100000000,999999999)}"},
        "it": {"country": "Italy 🇮🇹", "first": ["Leonardo", "Giulia", "Francesco"], "last": ["Rossi", "Russo", "Ferrari"], "streets": ["Via Roma", "Corso Vittorio Emanuele"], "cities": ["Rome", "Milan"], "states": ["Lazio", "Lombardy"], "zips": ["00100", "20100"], "phone": f"+39 3{random.randint(10,99)} {random.randint(1000000,9999999)}"},
        "jp": {"country": "Japan 🇯🇵", "first": ["Haruto", "Yui", "Sota"], "last": ["Sato", "Suzuki", "Takahashi"], "streets": ["Nagata-cho", "Oshiage"], "cities": ["Tokyo", "Osaka"], "states": ["Tokyo", "Osaka"], "zips": ["100-0001", "530-0001"], "phone": f"+81 90-{random.randint(1000,9999)}-{random.randint(1000,9999)}"},
        "kz": {"country": "Kazakhstan 🇰🇿", "first": ["Timur", "Aigerim", "Dias"], "last": ["Nurlan", "Omarov", "Kasenov"], "streets": ["Dostyk Ave", "Konaev St"], "cities": ["Astana", "Almaty"], "states": ["Astana City", "Almaty City"], "zips": ["010000", "050000"], "phone": f"+7 7{random.choice(['01','02','05','07','75','77'])} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}"},
        "my": {"country": "Malaysia 🇲🇾", "first": ["Ahmad", "Siti", "Wei"], "last": ["Tan", "Lee", "Wong"], "streets": ["Jalan Ampang", "Jalan Bukit Bintang"], "cities": ["Kuala Lumpur", "George Town"], "states": ["Wilayah Persekutuan", "Penang"], "zips": ["50450", "10200"], "phone": f"+60 1{random.randint(1,9)}-{random.randint(1000,9999)} {random.randint(1000,9999)}"},
        "mx": {"country": "Mexico 🇲🇽", "first": ["Mateo", "Sofia", "Santiago"], "last": ["Garcia", "Martinez", "Lopez"], "streets": ["Paseo de la Reforma", "Av. Insurgentes"], "cities": ["Mexico City", "Guadalajara"], "states": ["CDMX", "Jalisco"], "zips": ["06600", "44100"], "phone": f"+52 55 {random.randint(1000,9999)} {random.randint(1000,9999)}"},
        "ma": {"country": "Morocco 🇲🇦", "first": ["Youssef", "Kenza", "Mehdi"], "last": ["Alami", "Bennani", "Tazi"], "streets": ["Mohammed V Blvd", "Allal Ben Abdellah"], "cities": ["Casablanca", "Rabat"], "states": ["Casablanca-Settat", "Rabat-Salé-Kénitra"], "zips": ["20000", "10000"], "phone": f"+212 6{random.randint(10,99)} {random.randint(10000,99999)}"},
        "nz": {"country": "New Zealand 🇳🇿", "first": ["Oliver", "Isla", "Jack"], "last": ["Clark", "Wright", "Smith"], "streets": ["Queen Street", "Lambton Quay"], "cities": ["Auckland", "Wellington"], "states": ["Auckland", "Wellington"], "zips": ["1010", "6011"], "phone": f"+64 21 {random.randint(100,999)} {random.randint(1000,9999)}"},
        "pa": {"country": "Panama 🇵🇦", "first": ["Carlos", "Maria", "Jose"], "last": ["Perez", "Gonzalez", "Rodriguez"], "streets": ["Via España", "Calle 50"], "cities": ["Panama City", "San Miguelito"], "states": ["Panama", "San Miguelito"], "zips": ["0801", "0803"], "phone": f"+507 6{random.randint(100,999)}-{random.randint(1000,9999)}"},
        "pk": {"country": "Pakistan 🇵🇰", "first": ["Hamza", "Ayesha", "Muhammad"], "last": ["Khan", "Malik", "Ahmed"], "streets": ["Jinnah Avenue", "Mall Road"], "cities": ["Islamabad", "Karachi"], "states": ["ICT", "Sindh"], "zips": ["44000", "74000"], "phone": f"+92 3{random.choice(['00','33','45'])}-{random.randint(1000000,9999999)}"},
        "pe": {"country": "Peru 🇵🇪", "first": ["Diego", "Lucia", "Mateo"], "last": ["Flores", "Ramos", "Garcia"], "streets": ["Av. Larco", "Av. Javier Prado"], "cities": ["Lima", "Arequipa"], "states": ["Lima", "Arequipa"], "zips": ["15074", "04001"], "phone": f"+51 9{random.randint(10000000,99999999)}"},
        "pl": {"country": "Poland 🇵🇱", "first": ["Jakub", "Julia", "Jan"], "last": ["Nowak", "Kowalski", "Wisniewski"], "streets": ["Marszałkowska", "Krakowskie Przedmieście"], "cities": ["Warsaw", "Krakow"], "states": ["Masovian", "Lesser Poland"], "zips": ["00-001", "31-000"], "phone": f"+48 {random.randint(500,899)} {random.randint(100,999)} {random.randint(100,999)}"},
        "qa": {"country": "Qatar 🇶🇦", "first": ["Fahad", "Noora", "Nasser"], "last": ["Al-Thani", "Al-Kuwari", "Al-Mannai"], "streets": ["Corniche Street", "Al Sadd Street"], "cities": ["Doha", "Al Rayyan"], "states": ["Doha", "Al Rayyan"], "zips": ["00000", "11111"], "phone": f"+974 {random.choice([33,55,66,77])}{random.randint(100000,999999)}"},
        "sa": {"country": "Saudi Arabia 🇸🇦", "first": ["Salman", "Sara", "Faisal"], "last": ["Al-Saud", "Al-Otaibi", "Al-Qahtani"], "streets": ["King Fahd Road", "Tahlia Street"], "cities": ["Riyadh", "Jeddah"], "states": ["Riyadh", "Makkah"], "zips": ["11564", "21411"], "phone": f"+966 5{random.randint(0,9)} {random.randint(100,999)} {random.randint(1000,9999)}"},
        "sg": {"country": "Singapore 🇸🇬", "first": ["Wei", "Li", "Jie"], "last": ["Tan", "Lim", "Lee"], "streets": ["Orchard Road", "Marina Bay Link"], "cities": ["Singapore", "Jurong"], "states": ["Central", "West"], "zips": ["238888", "600101"], "phone": f"+65 {random.choice([8,9])}{random.randint(1000000,9999999)}"},
        "es": {"country": "Spain 🇪🇸", "first": ["Hugo", "Lucia", "Mateo"], "last": ["Garcia", "Martinez", "Lopez"], "streets": ["Gran Via", "Paseo de la Castellana"], "cities": ["Madrid", "Barcelona"], "states": ["Madrid", "Catalonia"], "zips": ["28001", "08001"], "phone": f"+34 6{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}"},
        "se": {"country": "Sweden 🇸🇪", "first": ["William", "Alice", "Liam"], "last": ["Andersson", "Johansson", "Karlsson"], "streets": ["Sveavägen", "Drottninggatan"], "cities": ["Stockholm", "Gothenburg"], "states": ["Stockholm", "Västra Götaland"], "zips": ["111 20", "411 10"], "phone": f"+46 7{random.randint(0,9)} {random.randint(1000000,9999999)}"},
        "ch": {"country": "Switzerland 🇨🇭", "first": ["Noah", "Mia", "Liam"], "last": ["Muller", "Meier", "Schmid"], "streets": ["Bahnhofstrasse", "Rue du Rhone"], "cities": ["Zurich", "Geneva"], "states": ["Zurich", "Geneva"], "zips": ["8001", "1201"], "phone": f"+41 7{random.choice([6,7,8,9])} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}"},
        "th": {"country": "Thailand 🇹🇭", "first": ["Somchai", "Suda", "Arthit"], "last": ["Saelim", "Wong", "Srisai"], "streets": ["Sukhumvit Road", "Silom Road"], "cities": ["Bangkok", "Chiang Mai"], "states": ["Bangkok", "Chiang Mai"], "zips": ["10110", "50000"], "phone": f"+66 8{random.randint(1,9)} {random.randint(1000,9999)} {random.randint(1000,9999)}"},
        "tr": {"country": "Turkiye 🇹🇷", "first": ["Yusuf", "Zeynep", "Mustafa"], "last": ["Yilmaz", "Kaya", "Demir"], "streets": ["Istiklal", "Ataturk Bulvari"], "cities": ["Istanbul", "Ankara"], "states": ["Istanbul", "Ankara"], "zips": ["34000", "06000"], "phone": f"+90 5{random.randint(10,59)} {random.randint(100,999)} {random.randint(1000,9999)}"},
        "uk": {"country": "United Kingdom 🇬🇧", "first": ["George", "Olivia", "Arthur"], "last": ["Smith", "Jones", "Williams"], "streets": ["High Street", "Station Road"], "cities": ["London", "Manchester"], "states": ["England", "Scotland"], "zips": ["SW1A 1AA", "M1 1AA"], "phone": f"+44 7{random.randint(100,999)} {random.randint(100000,999999)}"},
        "us": {"country": "United States 🇺🇸", "first": ["James", "Mary", "Robert"], "last": ["Smith", "Johnson", "Williams"], "streets": ["Broadway", "Main St"], "cities": ["New York", "Los Angeles"], "states": ["NY", "CA"], "zips": ["10001", "90001"], "phone": f"+1 ({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"}
    }
    
    data = loc_database.get(country_code, loc_database["us"])
    
    fname = random.choice(data["first"])
    lname = random.choice(data["last"])
    street = f"{random.randint(1,9999)} " + random.choice(data["streets"]).split(' ', 1)[-1]
    city = random.choice(data["cities"])
    state = random.choice(data["states"])
    zip_code = random.choice(data["zips"])
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
        f"IBAN: <code>{country}{check_dig}{bank_code}{acc_num}</code>\n"
        f"Length: <code>22</code>\n\n"
        f"Bank Code: <code>{bank_code}</code>\n"
        f"Account Number: <code>{acc_num}</code>\n"
        f"Check Digits: <code>{check_dig}</code>\n"
        f"BBAN: <code>{bank_code}{acc_num}</code>"
    )
    bot.reply_to(message, text, reply_markup=get_main_menu())

# --- Routing for Text, Auto-Detect & Buttons ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    add_user(message.from_user.id) 
    if is_banned(message.from_user.id): return
    text = message.text.strip()

    if text in ["🔐 Gen BIN", "/gen"]:
        bot.reply_to(message, "⏳ <b>BIN Generator</b>\nBIN သို့မဟုတ် Format ကို တိုက်ရိုက် ပို့ပေးပါ။\n(ဥပမာ - <code>412236</code> သို့မဟုတ် <code>62584005116|02|29</code>)", reply_markup=get_main_menu())
        return
    elif text in ["👉 Fake Address", "/fake"]:
        bot.reply_to(message, "⏳ <b>Fake Address</b>\nနိုင်ငံကုဒ် ပို့ပေးပါ။ (ဥပမာ - <code>us</code>, <code>de</code>, <code>jp</code>, <code>id</code>)\n\n💡 <i>နိုင်ငံစာရင်းကြည့်ရန် <code>list</code> ဟုရိုက်ပါ။</i>", reply_markup=get_main_menu())
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
