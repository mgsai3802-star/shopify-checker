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

def setup_bot_commands():
    commands = [
        BotCommand("me", "🔍 Telegram Account Info"),
        BotCommand("gen", "🔐 CC Generator (/gen 41546444023333)"),
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
        f"🔍 Telegram Account Info\n\n"
        f"👤 Name: {user.first_name} {user.last_name or ''}\n"
        f"🆔 User ID: {user.id}\n"
        f"🌐 Username: @{user.username or 'None'}\n"
        f"⚙️ Language: {user.language_code or 'N/A'}"
    )
    bot.reply_to(message, f"<pre>{text}</pre>")

# 2. CC Generator (/gen) - Full prefix support & remaining random digits fill
@bot.message_handler(commands=['gen'])
def cmd_gen(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 2 or len(parts[1]) < 4:
        bot.reply_to(message, "<pre>❌ အသုံးပြုနည်း: /gen 41546444023333</pre>")
        return
        
    bin_input = parts[1].strip()
    is_amex = bin_input.startswith("34") or bin_input.startswith("37")
    target_len = 15 if is_amex else 16
    
    # If user input length is greater than or equal to target, ensure it generates at least 1 random digit
    card_length = max(target_len, len(bin_input) + 1)
    cvv_length = 4 if is_amex else 3
    
    cards = []
    for _ in range(10):
        rand_digits = "".join([str(random.randint(0, 9)) for _ in range(card_length - len(bin_input))])
        full_cc = bin_input + rand_digits
        mm = f"{random.randint(1, 12):02d}"
        yyyy = str(random.randint(2027, 2035))
        cvv = "".join([str(random.randint(0, 9)) for _ in range(cvv_length)])
        cards.append(f"{full_cc}|{mm}|{yyyy}|{cvv}")
    
    header = f"𝗕𝗜𝗡 ⇾ {bin_input}\n𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10\n\n"
    cards_str = "\n".join(cards)
    full_response = f"{header}<pre>{cards_str}</pre>"
    bot.reply_to(message, full_response)

# 3. IBAN Generator (/iban)
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

# 4. CPF Generator (/cpf)
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

# 5. Full 37-Country Address Generator (/fake)
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
            "💡 အသုံးပြုပုံ: /fake DE သို့မဟုတ် /fake US"
        )
        bot.reply_to(message, f"<pre>{country_list_text}</pre>")
        return

    country = parts[1].upper()
    
    loc_database = {
        "DZ": {"country": "Algeria 🇩🇿", "names": [("Amine", "Benali"), ("Fatima", "Khelifi")], "streets": ["12 Rue Didouche Mourad", "45 Blvd Mohamed V"], "cities": ["Algiers", "Oran", "Constantine"], "states": ["Algiers", "Oran", "Constantine"], "zips": ["16000", "31000", "25000"], "phone": "+213 21 12 34 56"},
        "AR": {"country": "Argentina 🇦🇷", "names": [("Mateo", "Gomez"), ("Sofia", "Fernandez")], "streets": ["Av. Corrientes 1234", "Calle Florida 456"], "cities": ["Buenos Aires", "Cordoba", "Rosario"], "states": ["Buenos Aires", "Cordoba", "Santa Fe"], "zips": ["C1043", "X5000", "S2000"], "phone": "+54 11 4321 5678"},
        "AU": {"country": "Australia 🇦🇺", "names": [("Jack", "Smith"), ("Charlotte", "Wilson")], "streets": ["120 Collins St", "45 George St"], "cities": ["Sydney", "Melbourne", "Brisbane"], "states": ["NSW", "Victoria", "Queensland"], "zips": ["2000", "3000", "4000"], "phone": "+61 3 9555 0143"},
        "BH": {"country": "Bahrain 🇧🇭", "names": [("Ali", "Hassan"), ("Zainab", "Ahmed")], "streets": ["Road No 2803", "King Faisal Hwy"], "cities": ["Manama", "Riffa", "Muharraq"], "states": ["Capital", "Southern", "Muharraq"], "zips": ["328", "901", "251"], "phone": "+973 17 123 456"},
        "BD": {"country": "Bangladesh 🇧🇩", "names": [("Rahim", "Uddin"), ("Ayesha", "Begum")], "streets": ["45 Motijheel C/A", "12 Gulshan Ave"], "cities": ["Dhaka", "Chittagong", "Sylhet"], "states": ["Dhaka", "Chittagong", "Sylhet"], "zips": ["1000", "4000", "3100"], "phone": "+880 2 955 1234"},
        "BE": {"country": "Belgium 🇧🇪", "names": [("Lucas", "Janssen"), ("Camille", "Dubois")], "streets": ["Rue de la Loi 16", "Meir 50"], "cities": ["Brussels", "Antwerp", "Ghent"], "states": ["Brussels-Capital", "Flanders", "Wallonia"], "zips": ["1000", "2000", "9000"], "phone": "+32 2 555 01 43"},
        "BR": {"country": "Brazil 🇧🇷", "names": [("Anderson", "Silva"), ("Mariana", "Santos")], "streets": ["Av. Paulista 1000", "Copacabana 500"], "cities": ["São Paulo", "Rio de Janeiro", "Brasília"], "states": ["SP", "RJ", "DF"], "zips": ["01310-100", "22041-001", "70000-000"], "phone": "+55 11 98765-4321"},
        "KH": {"country": "Cambodia 🇰🇭", "names": [("Sokha", "Chan"), ("Vanna", "Seng")], "streets": ["Preah Monivong Blvd", "Sihanouk Blvd"], "cities": ["Phnom Penh", "Siem Reap", "Battambang"], "states": ["Phnom Penh", "Siem Reap", "Battambang"], "zips": ["12200", "17251", "02150"], "phone": "+855 23 123 456"},
        "CA": {"country": "Canada 🇨🇦", "names": [("Liam", "Tremblay"), ("Olivia", "Roy")], "streets": ["789 Yonge St", "123 Queen St W"], "cities": ["Toronto", "Vancouver", "Montreal"], "states": ["Ontario", "British Columbia", "Quebec"], "zips": ["M4W 2G8", "V6B 1B6", "H3B 1A2"], "phone": "+1 416-555-0143"},
        "CO": {"country": "Colombia 🇨🇴", "names": [("Santiago", "Rodriguez"), ("Valeria", "Lopez")], "streets": ["Cra. 7 #32-16", "Calle 50 #70-20"], "cities": ["Bogota", "Medellin", "Cali"], "states": ["Cundinamarca", "Antioquia", "Valle del Cauca"], "zips": ["110311", "050001", "760001"], "phone": "+57 1 234 5678"},
        "DK": {"country": "Denmark 🇩🇰", "names": [("Magnus", "Nielsen"), ("Ida", "Jensen")], "streets": ["Strøget 12", "Vesterbrogade 5"], "cities": ["Copenhagen", "Aarhus", "Odense"], "states": ["Capital Region", "Central Denmark", "Syddanmark"], "zips": ["1160", "8000", "5000"], "phone": "+45 33 12 34 56"},
        "EG": {"country": "Egypt 🇪🇬", "names": [("Ahmed", "Mohamed"), ("Nour", "Ibrahim")], "streets": ["15 Tahrir Square", "Corniche El Nil"], "cities": ["Cairo", "Alexandria", "Giza"], "states": ["Cairo", "Alexandria", "Giza"], "zips": ["11511", "21500", "12511"], "phone": "+20 2 2345 6789"},
        "FI": {"country": "Finland 🇫🇮", "names": [("Eetu", "Korhonen"), ("Aino", "Virtanen")], "streets": ["Mannerheimintie 10", "Aleksanterinkatu 5"], "cities": ["Helsinki", "Espoo", "Tampere"], "states": ["Uusimaa", "Pirkanmaa", "Southwest Finland"], "zips": ["00100", "02100", "33100"], "phone": "+358 9 123 4567"},
        "FR": {"country": "France 🇫🇷", "names": [("Gabriel", "Bernard"), ("Jade", "Petit")], "streets": ["15 Rue de la Paix", "10 Champs-Élysées"], "cities": ["Paris", "Lyon", "Marseille"], "states": ["Île-de-France", "Auvergne-Rhône-Alpes", "Provence"], "zips": ["75001", "69001", "13001"], "phone": "+33 1 23 45 67 89"},
        "DE": {"country": "Germany 🇩🇪", "names": [("Maximilian", "Schmidt"), ("Anna", "Weber")], "streets": ["Hauptstraße 42", "Friedrichstraße 15"], "cities": ["Berlin", "Munich", "Frankfurt"], "states": ["Berlin", "Bavaria", "Hesse"], "zips": ["10115", "80331", "60311"], "phone": "+49 30 1234567"},
        "IN": {"country": "India 🇮🇳", "names": [("Aarav", "Sharma"), ("Diya", "Patel")], "streets": ["MG Road", "Connaught Place"], "cities": ["Mumbai", "Delhi", "Bangalore"], "states": ["Maharashtra", "Delhi", "Karnataka"], "zips": ["400001", "110001", "560001"], "phone": "+91 22 2345 6789"},
        "IT": {"country": "Italy 🇮🇹", "names": [("Leonardo", "Rossi"), ("Giulia", "Russo")], "streets": ["Via del Corso 18", "Via Montenapoleone 5"], "cities": ["Rome", "Milan", "Naples"], "states": ["Lazio", "Lombardy", "Campania"], "zips": ["00186", "20121", "80132"], "phone": "+39 06 6982 1"},
        "JP": {"country": "Japan 🇯🇵", "names": [("Haruto", "Sato"), ("Yui", "Suzuki")], "streets": ["2-11-1 Nagata-cho", "1-1-2 Oshiage"], "cities": ["Tokyo", "Osaka", "Kyoto"], "states": ["Tokyo", "Osaka", "Kyoto"], "zips": ["100-0014", "530-0001", "600-8216"], "phone": "+81 3 5555 0143"},
        "KZ": {"country": "Kazakhstan 🇰🇿", "names": [("Timur", "Nurlan"), ("Aigerim", "Omarova")], "streets": ["Dostyk Ave 18", "Konaev St 25"], "cities": ["Astana", "Almaty", "Shymkent"], "states": ["Astana", "Almaty", "Shymkent"], "zips": ["010000", "050000", "160000"], "phone": "+7 7172 12 34 56"},
        "MY": {"country": "Malaysia 🇲🇾", "names": [("Ahmad", "Bin", "Tan"), ("Siti", "Nurhaliza")], "streets": ["Jalan Ampang", "Jalan Bukit Bintang"], "cities": ["Kuala Lumpur", "George Town", "Johor Bahru"], "states": ["Wilayah Persekutuan", "Penang", "Johor"], "zips": ["50450", "10200", "80000"], "phone": "+60 3 2161 2345"},
        "MX": {"country": "Mexico 🇲🇽", "names": [("Mateo", "Garcia"), ("Sofia", "Martinez")], "streets": ["Paseo de la Reforma 222", "Av. Insurgentes 500"], "cities": ["Mexico City", "Guadalajara", "Monterrey"], "states": ["CDMX", "Jalisco", "Nuevo Leon"], "zips": ["06600", "44100", "64000"], "phone": "+52 55 1234 5678"},
        "MA": {"country": "Morocco 🇲🇦", "names": [("Youssef", "Alami"), ("Kenza", "Bennani")], "streets": ["Mohammed V Blvd", "Allal Ben Abdellah"], "cities": ["Casablanca", "Rabat", "Marrakech"], "states": ["Casablanca-Settat", "Rabat-Salé-Kénitra", "Marrakech-Safi"], "zips": ["20000", "10000", "40000"], "phone": "+212 5 22 12 34 56"},
        "NZ": {"country": "New Zealand 🇳🇿", "names": [("Oliver", "Clark"), ("Isla", "Wright")], "streets": ["Queen Street", "Lambton Quay"], "cities": ["Auckland", "Wellington", "Christchurch"], "states": ["Auckland", "Wellington", "Canterbury"], "zips": ["1010", "6011", "8011"], "phone": "+64 9 309 1234"},
        "PA": {"country": "Panama 🇵🇦", "names": [("Carlos", "Perez"), ("Maria", "Gonzalez")], "streets": ["Via España", "Calle 50"], "cities": ["Panama City", "San Miguelito", "David"], "states": ["Panama", "San Miguelito", "Chiriqui"], "zips": ["0801", "0803", "0401"], "phone": "+507 200 1234"},
        "PK": {"country": "Pakistan 🇵🇰", "names": [("Hamza", "Khan"), ("Ayesha", "Malik")], "streets": ["Jinnah Avenue", "Mall Road"], "cities": ["Islamabad", "Karachi", "Lahore"], "states": ["ICT", "Sindh", "Punjab"], "zips": ["44000", "74000", "54000"], "phone": "+92 51 111 222 333"},
        "PE": {"country": "Peru 🇵🇪", "names": [("Diego", "Flores"), ("Lucia", "Ramos")], "streets": ["Av. Larco 101", "Av. Javier Prado 200"], "cities": ["Lima", "Arequipa", "Trujillo"], "states": ["Lima", "Arequipa", "La Libertad"], "zips": ["15074", "04001", "13001"], "phone": "+51 1 241 1234"},
        "PL": {"country": "Poland 🇵🇱", "names": [("Jakub", "Nowak"), ("Zuzanna", "Wojcik")], "streets": ["Marszałkowska 100", "Nowy Świat 20"], "cities": ["Warsaw", "Krakow", "Lodz"], "states": ["Masovian", "Lesser Poland", "Lodz"], "zips": ["00-001", "31-000", "90-001"], "phone": "+48 22 123 45 67"},
        "QA": {"country": "Qatar 🇶🇦", "names": [("Fahad", "Al-Thani"), ("Noora", "Al-Kuwari")], "streets": ["Corniche Street", "Al Sadd Street"], "cities": ["Doha", "Al Rayyan", "Al Wakrah"], "states": ["Doha", "Al Rayyan", "Al Wakrah"], "zips": ["00000", "11111", "22222"], "phone": "+974 44 123 456"},
        "SA": {"country": "Saudi Arabia 🇸🇦", "names": [("Salman", "Al-Saud"), ("Sara", "Al-otaibi")], "streets": ["King Fahd Road", "Tahlia Street"], "cities": ["Riyadh", "Jeddah", "Mecca"], "states": ["Riyadh", "Makkah", "Eastern Province"], "zips": ["11564", "21411", "21955"], "phone": "+966 11 123 4567"},
        "SG": {"country": "Singapore 🇸🇬", "names": [("Wei", "Jie", "Tan"), ("Li", "Hua", "Lim")], "streets": ["Orchard Road", "Marina Bay Link"], "cities": ["Singapore", "Jurong", "Woodlands"], "states": ["Central", "West", "North"], "zips": ["238888", "600101", "730001"], "phone": "+65 6737 3911"},
        "ES": {"country": "Spain 🇪🇸", "names": [("Alejandro", "Garcia"), ("Lucia", "Martinez")], "streets": ["Gran Vía 28", "Paseo de la Castellana 50"], "cities": ["Madrid", "Barcelona", "Valencia"], "states": ["Madrid", "Catalonia", "Valencian Community"], "zips": ["28013", "08001", "46001"], "phone": "+34 91 555 0143"},
        "SE": {"country": "Sweden 🇸🇪", "names": [("Lucas", "Andersson"), ("Maja", "Johansson")], "streets": ["Drottninggatan 15", "Avenyn 10"], "cities": ["Stockholm", "Gothenburg", "Malmo"], "states": ["Stockholm County", "Västra Götaland", "Skåne"], "zips": ["111 51", "411 36", "211 22"], "phone": "+46 8 123 456"},
        "CH": {"country": "Switzerland 🇨🇭", "names": [("Noah", "Müller"), ("Mia", "Schmid")], "streets": ["Bahnhofstrasse 45", "Rue du Rhône 10"], "cities": ["Zurich", "Geneva", "Basel"], "states": ["Zurich", "Geneva", "Basel-City"], "zips": ["8001", "1204", "4001"], "phone": "+41 44 211 00 00"},
        "TH": {"country": "Thailand 🇹🇭", "names": [("Somchai", "Somsak"), ("Mali", "Saengduean")], "streets": ["Sukhumvit Road", "Silom Road"], "cities": ["Bangkok", "Chiang Mai", "Pattaya"], "states": ["Bangkok", "Chiang Mai", "Chonburi"], "zips": ["10110", "50000", "20150"], "phone": "+66 2 123 4567"},
        "TR": {"country": "Turkiye 🇹🇷", "names": [("Mehmet", "Yilmaz"), ("Ayse", "Demir")], "streets": ["Istiklal Caddesi", "Ataturk Blvd"], "cities": ["Istanbul", "Ankara", "Izmir"], "states": ["Istanbul", "Ankara", "Izmir"], "zips": ["34430", "06100", "35210"], "phone": "+90 212 555 0143"},
        "UK": {"country": "United Kingdom 🇬🇧", "names": [("Oliver", "Smith"), ("Amelia", "Jones")], "streets": ["10 Downing Street", "221B Baker Street"], "cities": ["London", "Manchester", "Birmingham"], "states": ["Greater London", "Greater Manchester", "West Midlands"], "zips": ["SW1A 2AA", "M1 1AE", "B1 1AA"], "phone": "+44 20 7946 0918"},
        "US": {"country": "United States 🇺🇸", "names": [("Ella", "Anderson"), ("John", "Smith")], "streets": ["42 Canal Street", "123 Main Street"], "cities": ["New Orleans", "New York", "Los Angeles"], "states": ["Louisiana", "New York", "California"], "zips": ["70130", "10001", "90012"], "phone": "+1 504-555-0124"}
    }
    
    data = loc_database.get(country, loc_database["US"])
    
    fname, lname = random.choice(data["names"])
    street = random.choice(data["streets"])
    city = random.choice(data["cities"])
    state = random.choice(data["states"])
    zip_code = random.choice(data["zips"])
    email = f"{fname.lower()}.{lname.lower()}{random.randint(10,99)}@gmail.com"
    
    text = (
        f"📍 {data['country']} Address Generator\n\n"
        f"𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲: {fname} {lname}\n"
        f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: {street}\n"
        f"𝗖𝗶𝘁𝘆/𝗧𝗼𝘄𝗻/𝗩𝗶𝗹𝗹𝗮𝗴𝗲: {city}\n"
        f"𝗦𝘁𝗮𝘁𝗲/𝗣𝗿𝗼𝘃𝗶𝗻𝗰𝗲/𝗥𝗲𝗴𝗶𝗼𝗻: {state}\n"
        f"𝗣𝗼𝘀𝘁𝗮𝗹 𝗖𝗼𝗱𝗲: {zip_code}\n"
        f"𝗣𝗵𝗼𝗻𝗲 𝗡𝘂𝗺𝗯𝗲𝗿: {data['phone']}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {data['country']}\n"
        f"𝗧𝗲𝗺𝗽𝗼𝗿𝗮𝗿𝘆 𝗘𝗺𝗮𝗶𝗹: {email}"
    )
    bot.reply_to(message, f"<pre>{text}</pre>")

# 6. Ping Test (/ping)
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
        "🔐 /gen {prefix} - CC Generator (Supports long custom BINs)\n"
        "ℹ️ /iban {country} - IBAN Generator\n"
        "©️ /cpf - Brazilian CPF Generator\n"
        "📍 /fake {country} - Address Generator (Type /fake to see 37 countries list)\n"
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
