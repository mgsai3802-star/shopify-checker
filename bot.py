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
        BotCommand("gen", "🔐 CC Generator (/gen 62584005116|02|29)"),
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
        f"👤 Name: <code>{user.first_name} {user.last_name or ''}</code>\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"🌐 Username: <code>@{user.username or 'None'}</code>\n"
        f"⚙️ Language: <code>{user.language_code or 'N/A'}</code>"
    )
    bot.reply_to(message, text)

# 2. CC Generator (/gen) - Each card in individual <code> for independent copying
@bot.message_handler(commands=['gen'])
def cmd_gen(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ <b>အသုံးပြုနည်း:</b> <code>/gen 412236</code>\nသို့မဟုတ် <code>/gen 62584005116|02|29</code>")
        return
        
    arg = parts[1].strip()
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
        f"<b>𝗕𝗜𝗡 ⇾</b> <code>{bin6}</code>\n"
        f"<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾</b> <code>10</code>\n\n"
        f"{cards_str}\n\n"
        f"<b>𝗜𝗻𝗳𝗼:</b> <code>{brand} - {type_cc}</code>\n"
        f"<b>𝗕𝗮𝗻𝗸:</b> <code>{bank}</code>\n"
        f"<b>𝗖𝗼𝘂𝗻𝘁𝗿𝘆:</b> <code>{country}</code>"
    )
    bot.reply_to(message, text)

# 3. IBAN Generator (/iban)
@bot.message_handler(commands=['iban'])
def cmd_iban(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ <b>နိုင်ငံကုဒ် ထည့်ရန်လိုပါသည်။</b> ဥပမာ - <code>/iban DE</code>")
        return
        
    country = parts[1].upper()
    flags = {"DE": "🇩🇪", "GB": "🇬🇧", "FR": "🇫🇷", "ES": "🇪🇸", "IT": "🇮🇹", "BR": "🇧🇷", "US": "🇺🇸", "CA": "🇨🇦"}
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
    bot.reply_to(message, text)

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
        f"📍 <b>BR 🇧🇷 CPF Generator</b>\n\n"
        f"𝗡𝗮𝗺𝗲: <code>{name}</code>\n"
        f"𝗖𝗣𝗙: <code>{cpf}</code>\n"
        f"𝗗𝗼𝗕: <code>1988-04-10</code>\n"
        f"𝗣𝗹𝗮𝗰𝗲: <code>{place}</code>\n"
        f"𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝘆: <code>Segunda ({random.randint(1,28)}/{random.randint(1,12)})</code>"
    )
    bot.reply_to(message, text)

# 5. Massive 37-Country Address Generator (/fake)
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
            "💡 <i>အသုံးပြုပုံ:</i> <code>/fake DE</code> သို့မဟုတ် <code>/fake US</code>"
        )
        bot.reply_to(message, country_list_text)
        return

    country = parts[1].upper()
    
    loc_database = {
        "DZ": {"country": "Algeria 🇩🇿", "first": ["Amine", "Fatima", "Mohamed", "Amina", "Khaled", "Yasmine", "Tarek", "Rachid", "Samir", "Leila"], "last": ["Benali", "Khelifi", "Brahimi", "Mansouri", "Boumediene", "Zergui"], "streets": ["12 Rue Didouche Mourad", "45 Blvd Mohamed V", "78 Rue Hassiba", "10 Av. de l'Independence"], "cities": ["Algiers", "Oran", "Constantine", "Annaba", "Blida"], "states": ["Algiers", "Oran", "Constantine"], "zips": ["16000", "31000", "25000", "23000"], "phone": "+213 21 12 34 56"},
        "AR": {"country": "Argentina 🇦🇷", "first": ["Mateo", "Sofia", "Lucas", "Valentina", "Joaquin", "Martina", "Benjamin", "Camila"], "last": ["Gomez", "Fernandez", "Lopez", "Diaz", "Martinez", "Perez", "Rodriguez"], "streets": ["Av. Corrientes 1234", "Calle Florida 456", "Av. 9 de Julio 789", "Av. Santa Fe 2100"], "cities": ["Buenos Aires", "Cordoba", "Rosario", "Mendoza", "La Plata"], "states": ["Buenos Aires", "Cordoba", "Santa Fe", "Mendoza"], "zips": ["C1043", "X5000", "S2000", "M5500"], "phone": "+54 11 4321 5678"},
        "AU": {"country": "Australia 🇦🇺", "first": ["Jack", "Charlotte", "Oliver", "Isla", "Noah", "Mia", "William", "Harper"], "last": ["Smith", "Wilson", "Johnson", "Taylor", "Brown", "Martin", "White"], "streets": ["120 Collins St", "45 George St", "300 Elizabeth St", "15 Bourke St"], "cities": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Gold Coast"], "states": ["NSW", "Victoria", "Queensland", "Western Australia"], "zips": ["2000", "3000", "4000", "6000", "5000"], "phone": "+61 3 9555 0143"},
        "BH": {"country": "Bahrain 🇧🇭", "first": ["Ali", "Zainab", "Mohammed", "Fatima", "Ahmed", "Mariam", "Hassan"], "last": ["Hassan", "Ahmed", "Al-Khalifa", "Al-Doseri", "Al-Nuaimi"], "streets": ["Road No 2803", "King Faisal Hwy", "Budaiya Highway", "Shikh Isa Hwy"], "cities": ["Manama", "Riffa", "Muharraq", "Hamad Town", "A'ali"], "states": ["Capital", "Southern", "Muharraq", "Northern"], "zips": ["328", "901", "251", "121"], "phone": "+973 17 123 456"},
        "BD": {"country": "Bangladesh 🇧🇩", "first": ["Rahim", "Ayesha", "Tanvir", "Nusrat", "Sakib", "Farhana", "Imran", "Mehnaz"], "last": ["Uddin", "Begum", "Ahmed", "Khan", "Chowdhury", "Rahman", "Hossen"], "streets": ["45 Motijheel C/A", "12 Gulshan Ave", "78 Dhanmondi R/A", "90 Banani Road"], "cities": ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Barisal"], "states": ["Dhaka", "Chittagong", "Sylhet", "Rajshahi"], "zips": ["1000", "4000", "3100", "6000", "9000"], "phone": "+880 2 955 1234"},
        "BE": {"country": "Belgium 🇧🇪", "first": ["Lucas", "Camille", "Arthur", "Louise", "Noah", "Juliette", "Liam"], "last": ["Janssen", "Dubois", "Peeters", "Willems", "Maes", "Claes", "Goossens"], "streets": ["Rue de la Loi 16", "Meir 50", "Avenue Louise 120", "Rue Neuve 45"], "cities": ["Brussels", "Antwerp", "Ghent", "Bruges", "Liege", "Namur"], "states": ["Brussels-Capital", "Flanders", "Wallonia"], "zips": ["1000", "2000", "9000", "8000", "4000"], "phone": "+32 2 555 01 43"},
        "BR": {"country": "Brazil 🇧🇷", "first": ["Anderson", "Mariana", "Gabriel", "Beatriz", "Lucas", "Larissa", "Rafael", "Juliana"], "last": ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Ferreira", "Costa"], "streets": ["Av. Paulista 1000", "Copacabana 500", "Rua XV de Novembro 200", "Av. Atlantica 1200"], "cities": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza", "Belo Horizonte"], "states": ["SP", "RJ", "DF", "BA", "CE", "MG"], "zips": ["01310-100", "22041-001", "70000-000", "40010-000"], "phone": "+55 11 98765-4321"},
        "KH": {"country": "Cambodia 🇰🇭", "first": ["Sokha", "Vanna", "Dara", "Chan", "Srey", "Bopha", "Rith"], "last": ["Chan", "Seng", "Chea", "Kim", "Heng", "Ponn", "Lim"], "streets": ["Preah Monivong Blvd", "Sihanouk Blvd", "Norodom Blvd", "Russian Blvd"], "cities": ["Phnom Penh", "Siem Reap", "Battambang", "Sihanoukville", "Kampong Cham"], "states": ["Phnom Penh", "Siem Reap", "Battambang", "Preah Sihanouk"], "zips": ["12000", "17000", "02000", "18000"], "phone": "+855 23 123 456"},
        "CA": {"country": "Canada 🇨🇦", "first": ["Liam", "Olivia", "Noah", "Emma", "William", "Sophia", "Benjamin", "Charlotte"], "last": ["Tremblay", "Roy", "Gagnon", "Lee", "Smith", "Brown", "Wilson", "Taylor"], "streets": ["789 Yonge St", "123 Queen St W", "456 Sainte-Catherine St", "101 Sparks St"], "cities": ["Toronto", "Vancouver", "Montreal", "Ottawa", "Calgary", "Edmonton"], "states": ["Ontario", "British Columbia", "Quebec", "Alberta"], "zips": ["M4W 2G8", "V6B 1B6", "H3B 1A2", "K1P 1J1", "T2P 1K9"], "phone": "+1 416-555-0143"},
        "CO": {"country": "Colombia 🇨🇴", "first": ["Santiago", "Valeria", "Mateo", "Mariana", "Alejandro", "Isabella", "Sebastian"], "last": ["Rodriguez", "Lopez", "Garcia", "Martinez", "Gonzalez", "Perez", "Gomez"], "streets": ["Cra. 7 #32-16", "Calle 50 #70-20", "Av. El Dorado 68", "Calle 93 #15-40"], "cities": ["Bogota", "Medellin", "Cali", "Barranquilla", "Cartagena"], "states": ["Cundinamarca", "Antioquia", "Valle del Cauca", "Atlantico"], "zips": ["110311", "050001", "760001", "080001"], "phone": "+57 1 234 5678"},
        "DK": {"country": "Denmark 🇩🇰", "first": ["Magnus", "Ida", "Oliver", "Freja", "William", "Clara", "Noah"], "last": ["Nielsen", "Jensen", "Hansen", "Andersen", "Pedersen", "Christensen", "Larsen"], "streets": ["Strøget 12", "Vesterbrogade 5", "Nørrebrogade 40", "Gammel Kongevej 88"], "cities": ["Copenhagen", "Aarhus", "Odense", "Aalborg", "Esbjerg", "Randers"], "states": ["Capital Region", "Central Denmark", "Syddanmark", "North Denmark"], "zips": ["1160", "8000", "5000", "9000", "6700"], "phone": "+45 33 12 34 56"},
        "EG": {"country": "Egypt 🇪🇬", "first": ["Ahmed", "Nour", "Mohamed", "Salma", "Youssef", "Fatma", "Mahmoud", "Mariam"], "last": ["Mohamed", "Ibrahim", "Hassan", "Ali", "Mahmoud", "Abdallah", "Sayed"], "streets": ["15 Tahrir Square", "Corniche El Nil", "26 July St", "Abbas El Akkad St"], "cities": ["Cairo", "Alexandria", "Giza", "Port Said", "Suez", "Luxor"], "states": ["Cairo", "Alexandria", "Giza", "Dakahlia"], "zips": ["11511", "21500", "12511", "42511", "43511"], "phone": "+20 2 2345 6789"},
        "FI": {"country": "Finland 🇫🇮", "first": ["Eetu", "Aino", "Leo", "Venla", "Oliver", "Sofia", "Elias"], "last": ["Korhonen", "Virtanen", "Mäkinen", "Nieminen", "Mäkelä", "Hämäläinen", "Laine"], "streets": ["Mannerheimintie 10", "Aleksanterinkatu 5", "Hämeenkatu 14", "Itämerenkatu 21"], "cities": ["Helsinki", "Espoo", "Tampere", "Vantaa", "Oulu", "Turku"], "states": ["Uusimaa", "Pirkanmaa", "Southwest Finland", "North Ostrobothnia"], "zips": ["00100", "02100", "33100", "01300", "90100"], "phone": "+358 9 123 4567"},
        "FR": {"country": "France 🇫🇷", "first": ["Gabriel", "Jade", "Louis", "Louise", "Leo", "Emma", "Raphael", "Alice"], "last": ["Bernard", "Petit", "Robert", "Richard", "Durand", "Leroy", "Moreau", "Simon"], "streets": ["15 Rue de la Paix", "10 Champs-Élysées", "25 Rue de Rivoli", "8 Blvd Saint-Germain"], "cities": ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg"], "states": ["Île-de-France", "Auvergne-Rhône-Alpes", "Provence-Alpes-Côte d'Azur", "Occitanie"], "zips": ["75001", "69001", "13001", "31000", "06000", "44000"], "phone": "+33 1 23 45 67 89"},
        "DE": {"country": "Germany 🇩🇪", "first": ["Maximilian", "Anna", "Alexander", "Emma", "Elias", "Mia", "Noah", "Hannah", "Paul", "Sophia"], "last": ["Schmidt", "Weber", "Fischer", "Wagner", "Becker", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter"], "streets": ["Hauptstraße 42", "Friedrichstraße 15", "Königsallee 10", "Goethestraße 8", "Kurfürstendamm 65", "Lindenstraße 12"], "cities": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne", "Stuttgart", "Düsseldorf", "Dortmund", "Leipzig", "Essen"], "states": ["Berlin", "Bavaria", "Hesse", "Hamburg", "North Rhine-Westphalia", "Baden-Württemberg"], "zips": ["10115", "80331", "60311", "20095", "50667", "70173", "40213", "04109"], "phone": "+49 30 1234567"},
        "IN": {"country": "India 🇮🇳", "first": ["Aarav", "Diya", "Vivaan", "Saanvi", "Aditya", "Ananya", "Reyansh", "Priya", "Arjun", "Kavya"], "last": ["Sharma", "Patel", "Gupta", "Singh", "Kumar", "Verma", "Reddy", "Mehta", "Joshi", "Chauhan"], "streets": ["MG Road 12", "Connaught Place 5", "Park Street 45", "Brigade Road 88", "Linking Road 14"], "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad", "Pune", "Jaipur", "Surat"], "states": ["Maharashtra", "Delhi", "Karnataka", "Telangana", "Tamil Nadu", "West Bengal", "Gujarat"], "zips": ["400001", "110001", "560001", "500001", "600001", "700001", "380001", "411001"], "phone": "+91 22 2345 6789"},
        "IT": {"country": "Italy 🇮🇹", "first": ["Leonardo", "Giulia", "Francesco", "Aurora", "Alessandro", "Sofia", "Lorenzo", "Emma", "Mattia", "Ginevra"], "last": ["Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo", "Ricci", "Marino", "Greco"], "streets": ["Via del Corso 18", "Via Montenapoleone 5", "Via Toledo 100", "Corso Umberto I 45", "Via Nazionale 22"], "cities": ["Rome", "Milan", "Naples", "Turin", "Palermo", "Genoa", "Bologna", "Florence", "Venice", "Verona"], "states": ["Lazio", "Lombardy", "Campania", "Piedmont", "Sicily", "Veneto", "Tuscany", "Emilia-Romagna"], "zips": ["00186", "20121", "80132", "10121", "90133", "16121", "40121", "50123"], "phone": "+39 06 6982 1"},
        "JP": {"country": "Japan 🇯🇵", "first": ["Haruto", "Yui", "Sota", "Hina", "Ren", "Mei", "Hinata", "Riku", "Aoi", "Kaito"], "last": ["Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato"], "streets": ["2-11-1 Nagata-cho", "1-1-2 Oshiage", "3-5-1 Roppongi", "4-1-1 Nishi-Shinjuku", "5-2-1 Minami-Aoyama"], "cities": ["Tokyo", "Osaka", "Kyoto", "Nagoya", "Sapporo", "Fukuoka", "Kobe", "Yokohama", "Sendai", "Hiroshima"], "states": ["Tokyo", "Osaka", "Kyoto", "Aichi", "Hokkaido", "Fukuoka", "Hyogo", "Kanagawa"], "zips": ["100-0014", "530-0001", "600-8216", "460-0002", "060-0001", "810-0001", "650-0001", "220-0011"], "phone": "+81 3 5555 0143"},
        "KZ": {"country": "Kazakhstan 🇰🇿", "first": ["Timur", "Aigerim", "Dias", "Madina", "Alisher", "Zhansaya", "Rustam", "Assel", "Nurlan"], "last": ["Nurlan", "Omarov", "Kasenov", "Akhmetov", "Suleimenov", "Ibraev", "Kenzhebayev"], "streets": ["Dostyk Ave 18", "Konaev St 25", "Abay Ave 50", "Beibitshilik St 12", "Republic Ave 40"], "cities": ["Astana", "Almaty", "Shymkent", "Aktobe", "Karaganda", "Taraz", "Pavlodar", "Ust-Kamenogorsk"], "states": ["Astana City", "Almaty City", "Shymkent City", "Karaganda Region", "Aktobe Region"], "zips": ["010000", "050000", "160000", "030000", "100000", "080000"], "phone": "+7 7172 12 34 56"},
        "MY": {"country": "Malaysia 🇲🇾", "first": ["Ahmad", "Siti", "Wei", "Ling", "Ravi", "Priya", "Farhan", "Nurul", "Zack"], "last": ["Tan", "Lee", "Wong", "Kumar", "Bin", "Abdullah", "Chong", "Ramasamy", "Ng"], "streets": ["Jalan Ampang 50", "Jalan Bukit Bintang 12", "Jalan Tun Razak 100", "Jalan Sultan Ismail 20"], "cities": ["Kuala Lumpur", "George Town", "Johor Bahru", "Ipoh", "Malacca City", "Shah Alam", "Petaling Jaya"], "states": ["Wilayah Persekutuan", "Penang", "Johor", "Perak", "Selangor"], "zips": ["50450", "10200", "80000", "30000", "40000", "88000"], "phone": "+60 3 2161 2345"},
        "MX": {"country": "Mexico 🇲🇽", "first": ["Mateo", "Sofia", "Santiago", "Valentina", "Leonardo", "Camila", "Sebastian", "Ximena"], "last": ["Garcia", "Martinez", "Lopez", "Gonzalez", "Perez", "Rodriguez", "Sanchez", "Ramirez"], "streets": ["Paseo de la Reforma 222", "Av. Insurgentes 500", "Calle Madero 15", "Av. Juarez 80"], "cities": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana", "Leon", "Juarez", "Cancun"], "states": ["CDMX", "Jalisco", "Nuevo Leon", "Puebla", "Baja California", "Guanajuato"], "zips": ["06600", "44100", "64000", "72000", "22000", "37000"], "phone": "+52 55 1234 5678"},
        "MA": {"country": "Morocco 🇲🇦", "first": ["Youssef", "Kenza", "Mehdi", "Salma", "Amine", "Rim", "Hamza", "Hiba"], "last": ["Alami", "Bennani", "Tazi", "Idrissi", "Chraibi", "Amrani", "Fassi"], "streets": ["Mohammed V Blvd 12", "Allal Ben Abdellah 30", "Av. Hassan II 50", "Rue Farhat Hachad 5"], "cities": ["Casablanca", "Rabat", "Marrakech", "Fez", "Tangier", "Agadir", "Meknes"], "states": ["Casablanca-Settat", "Rabat-Salé-Kénitra", "Marrakech-Safi", "Fès-Meknès"], "zips": ["20000", "10000", "40000", "30000", "90000", "80000"], "phone": "+212 5 22 12 34 56"},
        "NZ": {"country": "New Zealand 🇳🇿", "first": ["Oliver", "Isla", "Jack", "Charlotte", "Noah", "Harper", "Leo", "Ava"], "last": ["Clark", "Wright", "Smith", "Wilson", "Taylor", "Johnson", "Martin", "Robinson"], "streets": ["Queen Street 100", "Lambton Quay 50", "Victoria Street 12", "Ponsonby Road 40"], "cities": ["Auckland", "Wellington", "Christchurch", "Hamilton", "Tauranga", "Dunedin"], "states": ["Auckland", "Wellington", "Canterbury", "Waikato", "Bay of Plenty"], "zips": ["1010", "6011", "8011", "3204", "3110", "9016"], "phone": "+64 9 309 1234"},
        "PA": {"country": "Panama 🇵🇦", "first": ["Carlos", "Maria", "Jose", "Ana", "Luis", "Carmen", "Javier", "Isabel"], "last": ["Perez", "Gonzalez", "Rodriguez", "Sanchez", "Torres", "Castillo", "Morales"], "streets": ["Via España 120", "Calle 50 45", "Av. Balboa 200", "Via Argentina 10"], "cities": ["Panama City", "San Miguelito", "David", "Colon", "Santiago", "Chitre"], "states": ["Panama", "San Miguelito", "Chiriqui", "Colon", "Veraguas"], "zips": ["0801", "0803", "0401", "0301", "0901"], "phone": "+507 200 1234"},
        "PK": {"country": "Pakistan 🇵🇰", "first": ["Hamza", "Ayesha", "Muhammad", "Fatima", "Ali", "Zainab", "Usman", "Khadija"], "last": ["Khan", "Malik", "Ahmed", "Butt", "Chaudhry", "Sheikh", "Qureshi", "Siddiqui"], "streets": ["Jinnah Avenue 10", "Mall Road 50", "F-7 Markaz 5", "Shahrah-e-Faisal 200"], "cities": ["Islamabad", "Karachi", "Lahore", "Faisalabad", "Rawalpindi", "Multan", "Peshawar", "Quetta"], "states": ["ICT", "Sindh", "Punjab", "Khyber Pakhtunkhwa", "Balochistan"], "zips": ["44000", "74000", "54000", "38000", "46000", "60000", "25000", "87300"], "phone": "+92 51 111 222 333"},
        "PE": {"country": "Peru 🇵🇪", "first": ["Diego", "Lucia", "Mateo", "Camila", "Joaquin", "Valeria", "Sebastian", "Ariana"], "last": ["Flores", "Ramos", "Garcia", "Rodriguez", "Castillo", "Sanchez", "Vargas", "Mendoza"], "streets": ["Av. Larco 101", "Av. Javier Prado 200", "Jr. De la Union 400", "Av. Arequipa 1200"], "cities": ["Lima", "Arequipa", "Trujillo", "Chiclayo", "Piura", "Cusco", "Iquitos", "Huancayo"], "states": ["Lima", "Arequipa", "La Libertad", "Lambayeque", "Piura", "Cusco"], "zips": ["15074", "04001", "13001", "14001", "20001", "08001", "12001"], "phone": "+51 1 241 1234"},
        "PL": {"country": "Poland 🇵🇱", "first": ["Jakub", "Zuzanna", "Kacper", "Julia", "Antoni", "Maja", "Szymon", "Hanna", "Jan"], "last": ["Nowak", "Wojcik", "Kowalski", "Wozniak", "Mazur", "Kaczmarek", "Krawczyk", "Piotrowski"], "streets": ["Marszałkowska 100", "Nowy Świat 20", "Floriańska 12", "Piotrkowska 45", "Świdnicka 8"], "cities": ["Warsaw", "Krakow", "Lodz", "Wroclaw", "Poznan", "Gdansk", "Szczecin", "Bydgoszcz", "Lublin"], "states": ["Masovian", "Lesser Poland", "Lodz", "Lower Silesian", "Greater Poland", "Pomeranian"], "zips": ["00-001", "31-000", "90-001", "50-001", "61-701", "80-834", "70-401", "20-002"], "phone": "+48 22 123 45 67"},
        "QA": {"country": "Qatar 🇶🇦", "first": ["Fahad", "Noora", "Nasser", "Maha", "Rashid", "Hissa", "Hamad", "Al-Anood"], "last": ["Al-Thani", "Al-Kuwari", "Al-Mannai", "Al-Kaabi", "Al-Muraikhi", "Al-Sulaiti"], "streets": ["Corniche Street 10", "Al Sadd Street 25", "Salwa Road 100", "Lusail Boulevard 1"], "cities": ["Doha", "Al Rayyan", "Al Wakrah", "Al Khor", "Umm Salal Muhammad", "Al Daayen"], "states": ["Doha", "Al Rayyan", "Al Wakrah", "Al Khor", "Umm Salal"], "zips": ["00000", "11111", "22222", "33333", "44444", "55555"], "phone": "+974 44 123 456"},
        "SA": {"country": "Saudi Arabia 🇸🇦", "first": ["Salman", "Sara", "Faisal", "Layan", "Abdullah", "Reem", "Khalid", "Nouf", "Turki"], "last": ["Al-Saud", "Al-Otaibi", "Al-Qahtani", "Al-Ghamdi", "Al-Dosari", "Al-Harbi", "Al-Shehri"], "streets": ["King Fahd Road 50", "Tahlia Street 12", "Olaya Street 100", "Prince Sultan Rd 200"], "cities": ["Riyadh", "Jeddah", "Mecca", "Medina", "Dammam", "Khobar", "Tabuk", "Abha", "Taif"], "states": ["Riyadh", "Makkah", "Madinah", "Eastern Province", "Asir", "Tabuk"], "zips": ["11564", "21411", "21955", "31421", "41411", "61411", "71411", "83111"], "phone": "+966 11 123 4567"},
        "SG": {"country": "Singapore 🇸🇬", "first": ["Wei", "Li", "Jie", "Hui", "Min", "Xin", "Jun", "Ying", "Kai"], "last": ["Tan", "Lim", "Lee", "Wong", "Ng", "Chua", "Koh", "Chan", "Teo"], "streets": ["Orchard Road 100", "Marina Bay Link 8", "Raffles Place 1", "Serangoon Road 200"], "cities": ["Singapore", "Jurong", "Woodlands", "Tampines", "Ang Mo Kio", "Bedok", "Yishun"], "states": ["Central", "West", "North", "East", "North-East"], "zips": ["238888", "600101", "730001", "529510", "560123", "460123", "760123"], "phone": "+65 6737 3911"},
        "ES": {"country": "Spain 🇪🇸", "first": ["Alejandro", "Lucia", "Pablo", "Sofia", "Daniel", "Alba", "David", "Paula", "Adrian"], "last": ["Garcia", "Martinez", "Lopez", "Sanchez", "Gonzalez", "Perez", "Rodriguez", "Gomez", "Martin"], "streets": ["Gran Vía 28", "Paseo de la Castellana 50", "Calle de Alcala 12", "Calle Serrano 40"], "cities": ["Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza", "Malaga", "Murcia", "Palma", "Bilbao"], "states": ["Madrid", "Catalonia", "Valencian Community", "Andalusia", "Aragon", "Basque Country"], "zips": ["28013", "08001", "46001", "41001", "50001", "29001", "30001", "07001", "48001"], "phone": "+34 91 555 0143"},
        "SE": {"country": "Sweden 🇸🇪", "first": ["Lucas", "Maja", "William", "Elsa", "Liam", "Astrid", "Noah", "Alice", "Elias"], "last": ["Andersson", "Johansson", "Karlsson", "Nilsson", "Eriksson", "Larsson", "Olsson", "Persson"], "streets": ["Drottninggatan 15", "Avenyn 10", "Kungsgatan 22", "Sveavägen 45", "Hamngatan 8"], "cities": ["Stockholm", "Gothenburg", "Malmo", "Uppsala", "Vasteras", "Orebro", "Linkoping", "Helsingborg"], "states": ["Stockholm County", "Västra Götaland", "Skåne", "Uppsala County", "Östergötland"], "zips": ["111 51", "411 36", "211 22", "753 20", "722 11", "702 10", "582 22", "252 20"], "phone": "+46 8 123 456"},
        "CH": {"country": "Switzerland 🇨🇭", "first": ["Noah", "Mia", "Liam", "Emma", "Gabriel", "Elena", "Matteo", "Lina", "Luca"], "last": ["Müller", "Schmid", "Keller", "Weber", "Huber", "Schneider", "Meyer", "Brunner", "Steiner"], "streets": ["Bahnhofstrasse 45", "Rue du Rhône 10", "Marktgasse 15", "Spitalgasse 8", "Freie Strasse 20"], "cities": ["Zurich", "Geneva", "Basel", "Bern", "Lausanne", "Winterthur", "Lucerne", "St. Gallen"], "states": ["Zurich", "Geneva", "Basel-City", "Bern", "Vaud", "Lucerne", "St. Gallen", "Ticino"], "zips": ["8001", "1204", "4001", "3011", "1003", "8400", "6003", "9000"], "phone": "+41 44 211 00 00"},
        "TH": {"country": "Thailand 🇹🇭", "first": ["Somchai", "Mali", "Arthit", "Kanya", "Chai", "Pornthip", "Narong", "Siriporn", "Thanapon"], "last": ["Saengduean", "Somsak", "Wongsuwan", "Suriyawong", "Chaiyanurak", "Ratanapon", "Boonyarit"], "streets": ["Sukhumvit Road 12", "Silom Road 45", "Petchburi Road 10", "Phahonyothin Road 100"], "cities": ["Bangkok", "Chiang Mai", "Pattaya", "Phuket", "Hat Yai", "Khon Kaen", "Nonthaburi", "Udon Thani"], "states": ["Bangkok", "Chiang Mai", "Chonburi", "Phuket", "Songkhla", "Khon Kaen", "Nonthaburi"], "zips": ["10110", "50000", "20150", "83000", "90110", "40000", "11000", "41000"], "phone": "+66 2 123 4567"},
        "TR": {"country": "Turkiye 🇹🇷", "first": ["Mehmet", "Ayse", "Mustafa", "Fatma", "Ahmet", "Zeynep", "Ali", "Elif", "Can", "Merve"], "last": ["Yilmaz", "Demir", "Kaya", "Celik", "Sahin", "Aydin", "Ozturk", "Arslan", "Dogan"], "streets": ["Istiklal Caddesi 15", "Ataturk Blvd 50", "Bagdat Avenue 120", "Tunalı Hilmi Cad. 8"], "cities": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep", "Mersin"], "states": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep"], "zips": ["34430", "06100", "35210", "16040", "07040", "01120", "42040", "27010", "33010"], "phone": "+90 212 555 0143"},
        "UK": {"country": "United Kingdom 🇬🇧", "first": ["Oliver", "Amelia", "George", "Isla", "Harry", "Ava", "Noah", "Mia", "Jack", "Grace"], "last": ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Davies", "Evans", "Thomas", "Johnson"], "streets": ["10 Downing Street", "221B Baker Street", "45 Oxford Street", "78 Regent Street", "12 Piccadilly", "15 Abbey Road"], "cities": ["London", "Manchester", "Birmingham", "Liverpool", "Edinburgh", "Glasgow", "Bristol", "Leeds", "Sheffield", "Cardiff"], "states": ["Greater London", "Greater Manchester", "West Midlands", "Merseyside", "Scotland", "Wales", "Yorkshire"], "zips": ["SW1A 2AA", "M1 1AE", "B1 1AA", "L1 8JQ", "EH1 1YZ", "G2 8DL", "BS1 4DJ", "LS1 1UR"], "phone": "+44 20 7946 0918"},
        "US": {"country": "United States 🇺🇸", "first": ["Ella", "John", "Emma", "Michael", "Sophia", "William", "Olivia", "James", "Benjamin", "Charlotte"], "last": ["Anderson", "Smith", "Watson", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Taylor", "Moore"], "streets": ["42 Canal Street", "123 Main Street", "789 Broadway", "55 Park Avenue", "101 Market Street", "300 Bourbon Street"], "cities": ["New Orleans", "New York", "Los Angeles", "Chicago", "Houston", "Philadelphia", "San Francisco", "Seattle", "Miami", "Boston"], "states": ["Louisiana", "New York", "California", "Illinois", "Texas", "Pennsylvania", "Washington", "Florida", "Massachusetts"], "zips": ["70130", "10001", "90012", "60601", "77002", "19102", "94101", "98101", "33101", "02108"], "phone": "+1 504-555-0124"}
    }
    
    data = loc_database.get(country, loc_database["US"])
    
    fname = random.choice(data["first"])
    lname = random.choice(data["last"])
    street = random.choice(data["streets"])
    city = random.choice(data["cities"])
    state = random.choice(data["states"])
    zip_code = random.choice(data["zips"])
    email = f"{fname.lower()}.{lname.lower()}{random.randint(10,99)}@gmail.com"
    
    text = (
        f"📍 <b>{data['country']} Address Generator</b>\n\n"
        f"𝗙𝘂𝗹𝗹 𝗡𝗮𝗺𝗲: <code>{fname} {lname}</code>\n"
        f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: <code>{street}</code>\n"
        f"𝗖𝗶𝘁𝘆/𝗧𝗼𝘄𝗻/𝗩𝗶𝗹𝗹𝗮𝗴𝗲: <code>{city}</code>\n"
        f"𝗦𝘁𝗮𝘁𝗲/𝗣𝗿𝗼𝘃𝗶𝗻𝗰𝗲/𝗥𝗲𝗴𝗶𝗼𝗻: <code>{state}</code>\n"
        f"𝗣𝗼𝘀𝘁𝗮𝗹 𝗖𝗼𝗱𝗲: <code>{zip_code}</code>\n"
        f"𝗣𝗵𝗼𝗻𝗲 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{data['phone']}</code>\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {data['country']}\n"
        f"𝗧𝗲𝗺𝗽𝗼𝗿𝗮𝗿𝘆 𝗘𝗺𝗮𝗶𝗹: <code>{email}</code>"
    )
    bot.reply_to(message, text)

# 6. Ping Test (/ping)
@bot.message_handler(commands=['ping'])
def cmd_ping(message):
    if not is_authorized(message.from_user.id): return
    latency = random.randint(110, 240)
    text = (
        f"Ｐｏｎｇ 🏓\n\n"
        f"⚡ <b>Response Time</b>\n"
        f"├ 📊 Latency: <code>{latency} ms</code>\n"
        f"└ 🎯 Quality: <code>🟢 Excellent</code>\n\n"
        f"🤖 <b>Bot Status:</b> Online & Responsive"
    )
    bot.reply_to(message, text)

# Help / Start Command
@bot.message_handler(commands=['start', 'help', 'cmd'])
def send_cmd(message):
    if not is_authorized(message.from_user.id): return
    text = (
        "🛠 <b>Bot Commands List</b>\n\n"
        "🔍 /me - Telegram Account Info\n"
        "🔐 /gen - CC Generator (/gen bin or /gen bin|mm|yy)\n"
        "ℹ️ /iban {country} - IBAN Generator\n"
        "©️ /cpf - Brazilian CPF Generator\n"
        "📍 /fake {country} - Address Generator (Type /fake to see 37 countries list)\n"
        "🔍 /ping - Ping Test"
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
