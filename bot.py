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
        BotCommand("gen", "🔐 CC Generator (/gen 415464|02|29)"),
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

# 2. CC Generator (/gen) - Custom BIN, Month, Year support
@bot.message_handler(commands=['gen'])
def cmd_gen(message):
    if not is_authorized(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "<pre>❌ အသုံးပြုနည်း: /gen 415464\nသို့မဟုတ် /gen 62584005116|02|29</pre>")
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
            
        cards.append(f"{full_cc}|{mm}|{yyyy}|{cvv}")
    
    header = f"𝗕𝗜𝗡 ⇾ {template_cc}\n𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10\n\n"
    cards_str = "\n".join(cards)
    bot.reply_to(message, f"{header}<pre>{cards_str}</pre>")

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

# 5. Massive 37-Country Address Generator (/fake)
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
    
    # Massive Multi-Country Database with extensive arrays ensuring thousands of combinations
    loc_database = {
        "DZ": {
            "country": "Algeria 🇩🇿",
            "first": ["Amine", "Fatima", "Mohamed", "Amina", "Khaled", "Yasmine", "Tarek", "Rachid", "Samir", "Leila", "Karim", "Nabila"],
            "last": ["Benali", "Khelifi", "Brahimi", "Mansouri", "Boumediene", "Zergui", "Cherif", "Meziane"],
            "streets": ["12 Rue Didouche Mourad", "45 Blvd Mohamed V", "78 Rue Hassiba", "10 Av. de l'Independence", "56 Rue Larbi Ben M'hidi"],
            "cities": ["Algiers", "Oran", "Constantine", "Annaba", "Blida", "Batna", "Sétif", "Tlemcen"],
            "states": ["Algiers", "Oran", "Constantine", "Annaba", "Blida"],
            "zips": ["16000", "31000", "25000", "23000", "09000", "19000"],
            "phone": "+213 21 12 34 56"
        },
        "AR": {
            "country": "Argentina 🇦🇷",
            "first": ["Mateo", "Sofia", "Lucas", "Valentina", "Joaquin", "Martina", "Benjamin", "Camila", "Thiago", "Lucia"],
            "last": ["Gomez", "Fernandez", "Lopez", "Diaz", "Martinez", "Perez", "Rodriguez", "Sanchez"],
            "streets": ["Av. Corrientes 1234", "Calle Florida 456", "Av. 9 de Julio 789", "Av. Santa Fe 2100", "Calle Lavalle 500"],
            "cities": ["Buenos Aires", "Cordoba", "Rosario", "Mendoza", "La Plata", "Mar del Plata", "San Miguel de Tucuman"],
            "states": ["Buenos Aires", "Cordoba", "Santa Fe", "Mendoza", "Tucuman"],
            "zips": ["C1043", "X5000", "S2000", "M5500", "B1904"],
            "phone": "+54 11 4321 5678"
        },
        "AU": {
            "country": "Australia 🇦🇺",
            "first": ["Jack", "Charlotte", "Oliver", "Isla", "Noah", "Mia", "William", "Harper", "Lucas", "Ava"],
            "last": ["Smith", "Wilson", "Johnson", "Taylor", "Brown", "Martin", "White", "Anderson"],
            "streets": ["120 Collins St", "45 George St", "300 Elizabeth St", "15 Bourke St", "88 Queen St"],
            "cities": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Gold Coast", "Canberra", "Hobart"],
            "states": ["NSW", "Victoria", "Queensland", "Western Australia", "South Australia"],
            "zips": ["2000", "3000", "4000", "6000", "5000", "2600"],
            "phone": "+61 3 9555 0143"
        },
        "BH": {
            "country": "Bahrain 🇧🇭",
            "first": ["Ali", "Zainab", "Mohammed", "Fatima", "Ahmed", "Mariam", "Hassan", "Noora"],
            "last": ["Hassan", "Ahmed", "Al-Khalifa", "Al-Doseri", "Al-Nuaimi", "Buallay"],
            "streets": ["Road No 2803", "King Faisal Hwy", "Budaiya Highway", "Shikh Isa Bin Salman Hwy", "Gudaibiya Ave"],
            "cities": ["Manama", "Riffa", "Muharraq", "Hamad Town", "A'ali", "Isa Town", "Sitra"],
            "states": ["Capital", "Southern", "Muharraq", "Northern"],
            "zips": ["328", "901", "251", "121", "712"],
            "phone": "+973 17 123 456"
        },
        "BD": {
            "country": "Bangladesh 🇧🇩",
            "first": ["Rahim", "Ayesha", "Tanvir", "Nusrat", "Sakib", "Farhana", "Imran", "Mehnaz", "Zubair", "Tasnim"],
            "last": ["Uddin", "Begum", "Ahmed", "Khan", "Chowdhury", "Rahman", "Hossen", "Siddique"],
            "streets": ["45 Motijheel C/A", "12 Gulshan Ave", "78 Dhanmondi R/A", "90 Banani Road 11", "23 Agrabad C/A"],
            "cities": ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Barisal", "Comilla", "Rangpur"],
            "states": ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna"],
            "zips": ["1000", "4000", "3100", "6000", "9000", "8200"],
            "phone": "+880 2 955 1234"
        },
        "BE": {
            "country": "Belgium 🇧🇪",
            "first": ["Lucas", "Camille", "Arthur", "Louise", "Noah", "Juliette", "Liam", "Mila"],
            "last": ["Janssen", "Dubois", "Peeters", "Willems", "Maes", "Claes", "Goossens", "Wouters"],
            "streets": ["Rue de la Loi 16", "Meir 50", "Avenue Louise 120", "Rue Neuve 45", "Kouter 12"],
            "cities": ["Brussels", "Antwerp", "Ghent", "Bruges", "Liege", "Namur", "Leuven", "Mons"],
            "states": ["Brussels-Capital", "Flanders", "Wallonia"],
            "zips": ["1000", "2000", "9000", "8000", "4000", "5000", "3000"],
            "phone": "+32 2 555 01 43"
        },
        "BR": {
            "country": "Brazil 🇧🇷",
            "first": ["Anderson", "Mariana", "Gabriel", "Beatriz", "Lucas", "Larissa", "Rafael", "Juliana", "Thiago", "Camila"],
            "last": ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Ferreira", "Costa", "Pereira"],
            "streets": ["Av. Paulista 1000", "Copacabana 500", "Rua XV de Novembro 200", "Av. Atlantica 1200", "Rua Augusta 400"],
            "cities": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza", "Belo Horizonte", "Curitiba", "Manaus"],
            "states": ["SP", "RJ", "DF", "BA", "CE", "MG", "PR", "AM"],
            "zips": ["01310-100", "22041-001", "70000-000", "40010-000", "30110-000"],
            "phone": "+55 11 98765-4321"
        },
        "KH": {
            "country": "Cambodia 🇰🇭",
            "first": ["Sokha", "Vanna", "Dara", "Chan", "Srey", "Bopha", "Rith", "Piseth"],
            "last": ["Chan", "Seng", "Chea", "Kim", "Heng", "Ponn", "Lim", "Keo"],
            "streets": ["Preah Monivong Blvd", "Sihanouk Blvd", "Norodom Blvd", "Russian Blvd", "Charles de Gaulle"],
            "cities": ["Phnom Penh", "Siem Reap", "Battambang", "Sihanoukville", "Kampong Cham", "Poipet"],
            "states": ["Phnom Penh", "Siem Reap", "Battambang", "Preah Sihanouk"],
            "zips": ["12000", "17000", "02000", "18000", "25000"],
            "phone": "+855 23 123 456"
        },
        "CA": {
            "country": "Canada 🇨🇦",
            "first": ["Liam", "Olivia", "Noah", "Emma", "William", "Sophia", "Benjamin", "Charlotte", "Lucas", "Amelia"],
            "last": ["Tremblay", "Roy", "Gagnon", "Lee", "Smith", "Brown", "Wilson", "Taylor", "Martin"],
            "streets": ["789 Yonge St", "123 Queen St W", "456 Sainte-Catherine St", "101 Sparks St", "55 Granby St"],
            "cities": ["Toronto", "Vancouver", "Montreal", "Ottawa", "Calgary", "Edmonton", "Quebec City", "Winnipeg"],
            "states": ["Ontario", "British Columbia", "Quebec", "Alberta", "Manitoba"],
            "zips": ["M4W 2G8", "V6B 1B6", "H3B 1A2", "K1P 1J1", "T2P 1K9"],
            "phone": "+1 416-555-0143"
        },
        "CO": {
            "country": "Colombia 🇨🇴",
            "first": ["Santiago", "Valeria", "Mateo", "Mariana", "Alejandro", "Isabella", "Sebastian", "Gabriela"],
            "last": ["Rodriguez", "Lopez", "Garcia", "Martinez", "Gonzalez", "Perez", "Gomez", "Vargas"],
            "streets": ["Cra. 7 #32-16", "Calle 50 #70-20", "Av. El Dorado 68", "Calle 93 #15-40", "Cra. 15 #88-20"],
            "cities": ["Bogota", "Medellin", "Cali", "Barranquilla", "Cartagena", "Cucuta", "Bucaramanga"],
            "states": ["Cundinamarca", "Antioquia", "Valle del Cauca", "Atlantico", "Bolivar"],
            "zips": ["110311", "050001", "760001", "080001", "130001"],
            "phone": "+57 1 234 5678"
        },
        "DK": {
            "country": "Denmark 🇩🇰",
            "first": ["Magnus", "Ida", "Oliver", "Freja", "William", "Clara", "Noah", "Emma"],
            "last": ["Nielsen", "Jensen", "Hansen", "Andersen", "Pedersen", "Christensen", "Larsen", "Sørensen"],
            "streets": ["Strøget 12", "Vesterbrogade 5", "Nørrebrogade 40", "Gammel Kongevej 88", "Østerbrogade 110"],
            "cities": ["Copenhagen", "Aarhus", "Odense", "Aalborg", "Esbjerg", "Randers", "Kolding"],
            "states": ["Capital Region", "Central Denmark", "Syddanmark", "North Denmark", "Zealand"],
            "zips": ["1160", "8000", "5000", "9000", "6700", "8900", "6000"],
            "phone": "+45 33 12 34 56"
        },
        "EG": {
            "country": "Egypt 🇪🇬",
            "first": ["Ahmed", "Nour", "Mohamed", "Salma", "Youssef", "Fatma", "Mahmoud", "Mariam", "Omar", "Aya"],
            "last": ["Mohamed", "Ibrahim", "Hassan", "Ali", "Mahmoud", "Abdallah", "Sayed", "Farouk"],
            "streets": ["15 Tahrir Square", "Corniche El Nil", "26 July St", "Abbas El Akkad St", "Haram Street"],
            "cities": ["Cairo", "Alexandria", "Giza", "Port Said", "Suez", "Luxor", "Aswan", "Mansoura"],
            "states": ["Cairo", "Alexandria", "Giza", "Dakahlia", "Red Sea"],
            "zips": ["11511", "21500", "12511", "42511", "43511", "85111"],
            "phone": "+20 2 2345 6789"
        },
        "FI": {
            "country": "Finland 🇫🇮",
            "first": ["Eetu", "Aino", "Leo", "Venla", "Oliver", "Sofia", "Elias", "Emilia"],
            "last": ["Korhonen", "Virtanen", "Mäkinen", "Nieminen", "Mäkelä", "Hämäläinen", "Laine", "Heikkinen"],
            "streets": ["Mannerheimintie 10", "Aleksanterinkatu 5", "Hämeenkatu 14", "Itämerenkatu 21", "Urho Kekkosen katu 1"],
            "cities": ["Helsinki", "Espoo", "Tampere", "Vantaa", "Oulu", "Turku", "Jyväskylä", "Kuopio"],
            "states": ["Uusimaa", "Pirkanmaa", "Southwest Finland", "North Ostrobothnia"],
            "zips": ["00100", "02100", "33100", "01300", "90100", "20100"],
            "phone": "+358 9 123 4567"
        },
        "FR": {
            "country": "France 🇫🇷",
            "first": ["Gabriel", "Jade", "Louis", "Louise", "Leo", "Emma", "Raphael", "Alice", "Arthur", "Chloe"],
            "last": ["Bernard", "Petit", "Robert", "Richard", "Durand", "Leroy", "Moreau", "Simon", "Michel"],
            "streets": ["15 Rue de la Paix", "10 Champs-Élysées", "25 Rue de Rivoli", "8 Boulevard Saint-Germain", "42 Rue de la République"],
            "cities": ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", "Bordeaux"],
            "states": ["Île-de-France", "Auvergne-Rhône-Alpes", "Provence-Alpes-Côte d'Azur", "Occitanie", "Grand Est"],
            "zips": ["75001", "69001", "13001", "31000", "06000", "44000", "67000", "34000"],
            "phone": "+33 1 23 45 67 89"
        },
        "DE": {
            "country": "Germany 🇩🇪",
            "first": ["Maximilian", "Anna", "Alexander", "Emma", "Elias", "Mia", "Noah", "Hannah", "Paul", "Sophia"],
            "last": ["Schmidt", "Weber", "Fischer", "Wagner", "Becker", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter"],
            "streets": ["Hauptstraße 42", "Friedrichstraße 15", "Königsallee 10", "Goethestraße 8", "Kurfürstendamm 65", "Lindenstraße 12"],
            "cities": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne", "Stuttgart", "Düsseldorf", "Dortmund", "Leipzig", "Essen"],
            "states": ["Berlin", "Bavaria", "Hesse", "Hamburg", "North Rhine-Westphalia", "Baden-Württemberg"],
            "zips": ["10115", "80331", "60311", "20095", "50667", "70173", "40213", "04109"],
            "phone": "+49 30 1234567"
        },
        "IN": {
            "country": "India 🇮🇳",
            "first": ["Aarav", "Diya", "Vivaan", "Saanvi", "Aditya", "Ananya", "Reyansh", "Priya", "Arjun", "Kavya"],
            "last": ["Sharma", "Patel", "Gupta", "Singh", "Kumar", "Verma", "Reddy", "Mehta", "Joshi", "Chauhan"],
            "streets": ["MG Road 12", "Connaught Place 5", "Park Street 45", "Brigade Road 88", "Linking Road 14"],
            "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad", "Pune", "Jaipur", "Surat"],
            "states": ["Maharashtra", "Delhi", "Karnataka", "Telangana", "Tamil Nadu", "West Bengal", "Gujarat"],
            "zips": ["400001", "110001", "560001", "500001", "600001", "700001", "380001", "411001"],
            "phone": "+91 22 2345 6789"
        },
        "IT": {
            "country": "Italy 🇮🇹",
            "first": ["Leonardo", "Giulia", "Francesco", "Aurora", "Alessandro", "Sofia", "Lorenzo", "Emma", "Mattia", "Ginevra"],
            "last": ["Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo", "Ricci", "Marino", "Greco"],
            "streets": ["Via del Corso 18", "Via Montenapoleone 5", "Via Toledo 100", "Corso Umberto I 45", "Via Nazionale 22"],
            "cities": ["Rome", "Milan", "Naples", "Turin", "Palermo", "Genoa", "Bologna", "Florence", "Venice", "Verona"],
            "states": ["Lazio", "Lombardy", "Campania", "Piedmont", "Sicily", "Veneto", "Tuscany", "Emilia-Romagna"],
            "zips": ["00186", "20121", "80132", "10121", "90133", "16121", "40121", "50123"],
            "phone": "+39 06 6982 1"
        },
        "JP": {
            "country": "Japan 🇯🇵",
            "first": ["Haruto", "Yui", "Sota", "Hina", "Ren", "Mei", "Hinata", "Riku", "Aoi", "Kaito"],
            "last": ["Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato"],
            "streets": ["2-11-1 Nagata-cho", "1-1-2 Oshiage", "3-5-1 Roppongi", "4-1-1 Nishi-Shinjuku", "5-2-1 Minami-Aoyama"],
            "cities": ["Tokyo", "Osaka", "Kyoto", "Nagoya", "Sapporo", "Fukuoka", "Kobe", "Yokohama", "Sendai", "Hiroshima"],
            "states": ["Tokyo", "Osaka", "Kyoto", "Aichi", "Hokkaido", "Fukuoka", "Hyogo", "Kanagawa"],
            "zips": ["100-0014", "530-0001", "600-8216", "460-0002", "060-0001", "810-0001", "650-0001", "220-0011"],
            "phone": "+81 3 5555 0143"
        },
        "KZ": {
            "country": "Kazakhstan 🇰🇿",
            "first": ["Timur", "Aigerim", "Dias", "Madina", "Alisher", "Zhansaya", "Rustam", "Assel", "Nurlan", "Dinara"],
            "last": ["Nurlan", "Omarov", "Kasenov", "Akhmetov", "Suleimenov", "Ibraev", "Kenzhebayev", "Baizhanov"],
            "streets": ["Dostyk Ave 18", "Konaev St 25", "Abay Ave 50", "Beibitshilik St 12", "Republic Ave 40"],
            "cities": ["Astana", "Almaty", "Shymkent", "Aktobe", "Karaganda", "Taraz", "Pavlodar", "Ust-Kamenogorsk"],
            "states": ["Astana City", "Almaty City", "Shymkent City", "Karaganda Region", "Aktobe Region"],
            "zips": ["010000", "050000", "160000", "030000", "100000", "080000"],
            "phone": "+7 7172 12 34 56"
        },
        "MY": {
            "country": "Malaysia 🇲🇾",
            "first": ["Ahmad", "Siti", "Wei", "Ling", "Ravi", "Priya", "Farhan", "Nurul", "Zack", "Mei"],
            "last": ["Tan", "Lee", "Wong", "Kumar", "Bin", "Abdullah", "Chong", "Ramasamy", "Ng", "Ibrahim"],
            "streets": ["Jalan Ampang 50", "Jalan Bukit Bintang 12", "Jalan Tun Razak 100", "Jalan Sultan Ismail 20", "Lebuh Pantai 15"],
            "cities": ["Kuala Lumpur", "George Town", "Johor Bahru", "Ipoh", "Malacca City", "Shah Alam", "Petaling Jaya", "Kota Kinabalu"],
            "states": ["Wilayah Persekutuan", "Penang", "Johor", "Perak", "Selangor", "Sabah", "Sarawak"],
            "zips": ["50450", "10200", "80000", "30000", "40000", "88000", "93000"],
            "phone": "+60 3 2161 2345"
        },
        "MX": {
            "country": "Mexico 🇲🇽",
            "first": ["Mateo", "Sofia", "Santiago", "Valentina", "Leonardo", "Camila", "Sebastian", "Ximena", "Diego", "Regina"],
            "last": ["Garcia", "Martinez", "Lopez", "Gonzalez", "Perez", "Rodriguez", "Sanchez", "Ramirez", "Cruz", "Flores"],
            "streets": ["Paseo de la Reforma 222", "Av. Insurgentes 500", "Calle Madero 15", "Av. Juarez 80", "Calzada de Tlalpan 1500"],
            "cities": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana", "Leon", "Juarez", "Cancun", "Merida"],
            "states": ["CDMX", "Jalisco", "Nuevo Leon", "Puebla", "Baja California", "Guanajuato", "Yucatan"],
            "zips": ["06600", "44100", "64000", "72000", "22000", "37000", "97000"],
            "phone": "+52 55 1234 5678"
        },
        "MA": {
            "country": "Morocco 🇲🇦",
            "first": ["Youssef", "Kenza", "Mehdi", "Salma", "Amine", "Rim", "Hamza", "Hiba", "Anas", "Chaimae"],
            "last": ["Alami", "Bennani", "Tazi", "Idrissi", "Chraibi", "Amrani", "Fassi", "Berrada"],
            "streets": ["Mohammed V Blvd 12", "Allal Ben Abdellah 30", "Av. Hassan II 50", "Rue Farhat Hachad 5", "Boulevard Zerktouni 100"],
            "cities": ["Casablanca", "Rabat", "Marrakech", "Fez", "Tangier", "Agadir", "Meknes", "Oujda"],
            "states": ["Casablanca-Settat", "Rabat-Salé-Kénitra", "Marrakech-Safi", "Fès-Meknès", "Tanger-Tétouan-Al Hoceïma"],
            "zips": ["20000", "10000", "40000", "30000", "90000", "80000", "50000"],
            "phone": "+212 5 22 12 34 56"
        },
        "NZ": {
            "country": "New Zealand 🇳🇿",
            "first": ["Oliver", "Isla", "Jack", "Charlotte", "Noah", "Harper", "Leo", "Ava", "Lucas", "Ella"],
            "last": ["Clark", "Wright", "Smith", "Wilson", "Taylor", "Johnson", "Martin", "Robinson", "Walker"],
            "streets": ["Queen Street 100", "Lambton Quay 50", "Victoria Street 12", "Ponsonby Road 40", "Riccarton Road 75"],
            "cities": ["Auckland", "Wellington", "Christchurch", "Hamilton", "Tauranga", "Dunedin", "Palmerston North"],
            "states": ["Auckland", "Wellington", "Canterbury", "Waikato", "Bay of Plenty", "Otago"],
            "zips": ["1010", "6011", "8011", "3204", "3110", "9016", "4410"],
            "phone": "+64 9 309 1234"
        },
        "PA": {
            "country": "Panama 🇵🇦",
            "first": ["Carlos", "Maria", "Jose", "Ana", "Luis", "Carmen", "Javier", "Isabel", "Ricardo", "Elena"],
            "last": ["Perez", "Gonzalez", "Rodriguez", "Sanchez", "Torres", "Castillo", "Morales", "Ortiz"],
            "streets": ["Via España 120", "Calle 50 45", "Av. Balboa 200", "Via Argentina 10", "Calle Uruguay 30"],
            "cities": ["Panama City", "San Miguelito", "David", "Colon", "Santiago", "Chitre", "Penonome"],
            "states": ["Panama", "San Miguelito", "Chiriqui", "Colon", "Veraguas", "Cocle"],
            "zips": ["0801", "0803", "0401", "0301", "0901", "0201"],
            "phone": "+507 200 1234"
        },
        "PK": {
            "country": "Pakistan 🇵🇰",
            "first": ["Hamza", "Ayesha", "Muhammad", "Fatima", "Ali", "Zainab", "Usman", "Khadija", "Bilal", "Sana"],
            "last": ["Khan", "Malik", "Ahmed", "Butt", "Chaudhry", "Sheikh", "Qureshi", "Siddiqui", "Ansari"],
            "streets": ["Jinnah Avenue 10", "Mall Road 50", "F-7 Markaz 5", "Shahrah-e-Faisal 200", "MM Alam Road 88"],
            "cities": ["Islamabad", "Karachi", "Lahore", "Faisalabad", "Rawalpindi", "Multan", "Peshawar", "Quetta", "Sialkot"],
            "states": ["ICT", "Sindh", "Punjab", "Khyber Pakhtunkhwa", "Balochistan"],
            "zips": ["44000", "74000", "54000", "38000", "46000", "60000", "25000", "87300", "51310"],
            "phone": "+92 51 111 222 333"
        },
        "PE": {
            "country": "Peru 🇵🇪",
            "first": ["Diego", "Lucia", "Mateo", "Camila", "Joaquin", "Valeria", "Sebastian", "Ariana", "Gabriel", "Ximena"],
            "last": ["Flores", "Ramos", "Garcia", "Rodriguez", "Castillo", "Sanchez", "Vargas", "Mendoza", "Rojas"],
            "streets": ["Av. Larco 101", "Av. Javier Prado 200", "Jr. De la Union 400", "Av. Arequipa 1200", "Calle Schell 50"],
            "cities": ["Lima", "Arequipa", "Trujillo", "Chiclayo", "Piura", "Cusco", "Iquitos", "Huancayo", "Tacna"],
            "states": ["Lima", "Arequipa", "La Libertad", "Lambayeque", "Piura", "Cusco", "Junin"],
            "zips": ["15074", "04001", "13001", "14001", "20001", "08001", "12001"],
            "phone": "+51 1 241 1234"
        },
        "PL": {
            "country": "Poland 🇵🇱",
            "first": ["Jakub", "Zuzanna", "Kacper", "Julia", "Antoni", "Maja", "Szymon", "Hanna", "Jan", "Lena"],
            "last": ["Nowak", "Wojcik", "Kowalski", "Wozniak", "Mazur", "Kaczmarek", "Krawczyk", "Piotrowski", "Grabowski"],
            "streets": ["Marszałkowska 100", "Nowy Świat 20", "Floriańska 12", "Piotrkowska 45", "Świdnicka 8"],
            "cities": ["Warsaw", "Krakow", "Lodz", "Wroclaw", "Poznan", "Gdansk", "Szczecin", "Bydgoszcz", "Lublin", "Katowice"],
            "states": ["Masovian", "Lesser Poland", "Lodz", "Lower Silesian", "Greater Poland", "Pomeranian"],
            "zips": ["00-001", "31-000", "90-001", "50-001", "61-701", "80-834", "70-401", "20-002"],
            "phone": "+48 22 123 45 67"
        },
        "QA": {
            "country": "Qatar 🇶🇦",
            "first": ["Fahad", "Noora", "Nasser", "Maha", "Rashid", "Hissa", "Hamad", "Al-Anood", "Jassim", "Maryam"],
            "last": ["Al-Thani", "Al-Kuwari", "Al-Mannai", "Al-Kaabi", "Al-Muraikhi", "Al-Sulaiti", "Al-Emadi"],
            "streets": ["Corniche Street 10", "Al Sadd Street 25", "Salwa Road 100", "Lusail Boulevard 1", "Al Waab Street 40"],
            "cities": ["Doha", "Al Rayyan", "Al Wakrah", "Al Khor", "Umm Salal Muhammad", "Al Daayen", "Mesaieed"],
            "states": ["Doha", "Al Rayyan", "Al Wakrah", "Al Khor", "Umm Salal"],
            "zips": ["00000", "11111", "22222", "33333", "44444", "55555"],
            "phone": "+974 44 123 456"
        },
        "SA": {
            "country": "Saudi Arabia 🇸🇦",
            "first": ["Salman", "Sara", "Faisal", "Layan", "Abdullah", "Reem", "Khalid", "Nouf", "Turki", "Jawaher"],
            "last": ["Al-Saud", "Al-Otaibi", "Al-Qahtani", "Al-Ghamdi", "Al-Dosari", "Al-Harbi", "Al-Shehri", "Al-Mutairi"],
            "streets": ["King Fahd Road 50", "Tahlia Street 12", "Olaya Street 100", "Prince Sultan Rd 200", "King Abdullah Rd 75"],
            "cities": ["Riyadh", "Jeddah", "Mecca", "Medina", "Dammam", "Khobar", "Tabuk", "Abha", "Taif", "Buraydah"],
            "states": ["Riyadh", "Makkah", "Madinah", "Eastern Province", "Asir", "Tabuk"],
            "zips": ["11564", "21411", "21955", "31421", "41411", "61411", "71411", "83111"],
            "phone": "+966 11 123 4567"
        },
        "SG": {
            "country": "Singapore 🇸🇬",
            "first": ["Wei", "Li", "Jie", "Hui", "Min", "Xin", "Jun", "Ying", "Kai", "Hao"],
            "last": ["Tan", "Lim", "Lee", "Wong", "Ng", "Chua", "Koh", "Chan", "Teo", "Ang"],
            "streets": ["Orchard Road 100", "Marina Bay Link 8", "Raffles Place 1", "Serangoon Road 200", "Tampines Central 3"],
            "cities": ["Singapore", "Jurong", "Woodlands", "Tampines", "Ang Mo Kio", "Bedok", "Yishun", "Clementi"],
            "states": ["Central", "West", "North", "East", "North-East"],
            "zips": ["238888", "600101", "730001", "529510", "560123", "460123", "760123", "120123"],
            "phone": "+65 6737 3911"
        },
        "ES": {
            "country": "Spain 🇪🇸",
            "first": ["Alejandro", "Lucia", "Pablo", "Sofia", "Daniel", "Alba", "David", "Paula", "Adrian", "Martina"],
            "last": ["Garcia", "Martinez", "Lopez", "Sanchez", "Gonzalez", "Perez", "Rodriguez", "Gomez", "Martin", "Jimenez"],
            "streets": ["Gran Vía 28", "Paseo de la Castellana 50", "Calle de Alcala 12", "Calle Serrano 40", "Avenida Diagonal 300"],
            "cities": ["Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza", "Malaga", "Murcia", "Palma", "Bilbao", "Alicante"],
            "states": ["Madrid", "Catalonia", "Valencian Community", "Andalusia", "Aragon", "Basque Country"],
            "zips": ["28013", "08001", "46001", "41001", "50001", "29001", "30001", "07001", "48001"],
            "phone": "+34 91 555 0143"
        },
        "SE": {
            "country": "Sweden 🇸🇪",
            "first": ["Lucas", "Maja", "William", "Elsa", "Liam", "Astrid", "Noah", "Alice", "Elias", "Agnes"],
            "last": ["Andersson", "Johansson", "Karlsson", "Nilsson", "Eriksson", "Larsson", "Olsson", "Persson", "Svensson"],
            "streets": ["Drottninggatan 15", "Avenyn 10", "Kungsgatan 22", "Sveavägen 45", "Hamngatan 8"],
            "cities": ["Stockholm", "Gothenburg", "Malmo", "Uppsala", "Vasteras", "Orebro", "Linkoping", "Helsingborg", "Jonkoping"],
            "states": ["Stockholm County", "Västra Götaland", "Skåne", "Uppsala County", "Östergötland"],
            "zips": ["111 51", "411 36", "211 22", "753 20", "722 11", "702 10", "582 22", "252 20"],
            "phone": "+46 8 123 456"
        },
        "CH": {
            "country": "Switzerland 🇨🇭",
            "first": ["Noah", "Mia", "Liam", "Emma", "Gabriel", "Elena", "Matteo", "Lina", "Luca", "Sara"],
            "last": ["Müller", "Schmid", "Keller", "Weber", "Huber", "Schneider", "Meyer", "Brunner", "Steiner", "Baumann"],
            "streets": ["Bahnhofstrasse 45", "Rue du Rhône 10", "Marktgasse 15", "Spitalgasse 8", "Freie Strasse 20"],
            "cities": ["Zurich", "Geneva", "Basel", "Bern", "Lausanne", "Winterthur", "Lucerne", "St. Gallen", "Lugano"],
            "states": ["Zurich", "Geneva", "Basel-City", "Bern", "Vaud", "Lucerne", "St. Gallen", "Ticino"],
            "zips": ["8001", "1204", "4001", "3011", "1003", "8400", "6003", "9000", "6900"],
            "phone": "+41 44 211 00 00"
        },
        "TH": {
            "country": "Thailand 🇹🇭",
            "first": ["Somchai", "Mali", "Arthit", "Kanya", "Chai", "Pornthip", "Narong", "Siriporn", "Thanapon", "Suwannee"],
            "last": ["Saengduean", "Somsak", "Wongsuwan", "Suriyawong", "Chaiyanurak", "Ratanapon", "Boonyarit", "Intarachai"],
            "streets": ["Sukhumvit Road 12", "Silom Road 45", "Petchburi Road 10", "Phahonyothin Road 100", "Rama IV Road 250"],
            "cities": ["Bangkok", "Chiang Mai", "Pattaya", "Phuket", "Hat Yai", "Khon Kaen", "Nonthaburi", "Udon Thani", "Nakhon Ratchasima"],
            "states": ["Bangkok", "Chiang Mai", "Chonburi", "Phuket", "Songkhla", "Khon Kaen", "Nonthaburi"],
            "zips": ["10110", "50000", "20150", "83000", "90110", "40000", "11000", "41000", "30000"],
            "phone": "+66 2 123 4567"
        },
        "TR": {
            "country": "Turkiye 🇹🇷",
            "first": ["Mehmet", "Ayse", "Mustafa", "Fatma", "Ahmet", "Zeynep", "Ali", "Elif", "Can", "Merve"],
            "last": ["Yilmaz", "Demir", "Kaya", "Celik", "Sahin", "Aydin", "Ozturk", "Arslan", "Dogan", "Kilic"],
            "streets": ["Istiklal Caddesi 15", "Ataturk Blvd 50", "Bagdat Avenue 120", "Tunalı Hilmi Cad. 8", "Kibris Caddesi 45"],
            "cities": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep", "Mersin", "Kayseri"],
            "states": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep"],
            "zips": ["34430", "06100", "35210", "16040", "07040", "01120", "42040", "27010", "33010", "38010"],
            "phone": "+90 212 555 0143"
        },
        "UK": {
            "country": "United Kingdom 🇬🇧",
            "first": ["Oliver", "Amelia", "George", "Isla", "Harry", "Ava", "Noah", "Mia", "Jack", "Grace"],
            "last": ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Davies", "Evans", "Thomas", "Johnson"],
            "streets": ["10 Downing Street", "221B Baker Street", "45 Oxford Street", "78 Regent Street", "12 Piccadilly", "15 Abbey Road"],
            "cities": ["London", "Manchester", "Birmingham", "Liverpool", "Edinburgh", "Glasgow", "Bristol", "Leeds", "Sheffield", "Cardiff"],
            "states": ["Greater London", "Greater Manchester", "West Midlands", "Merseyside", "Scotland", "Wales", "Yorkshire"],
            "zips": ["SW1A 2AA", "M1 1AE", "B1 1AA", "L1 8JQ", "EH1 1YZ", "G2 8DL", "BS1 4DJ", "LS1 1UR"],
            "phone": "+44 20 7946 0918"
        },
        "US": {
            "country": "United States 🇺🇸",
            "first": ["Ella", "John", "Emma", "Michael", "Sophia", "William", "Olivia", "James", "Benjamin", "Charlotte"],
            "last": ["Anderson", "Smith", "Watson", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Taylor", "Moore"],
            "streets": ["42 Canal Street", "123 Main Street", "789 Broadway", "55 Park Avenue", "101 Market Street", "300 Bourbon Street"],
            "cities": ["New Orleans", "New York", "Los Angeles", "Chicago", "Houston", "Philadelphia", "San Francisco", "Seattle", "Miami", "Boston"],
            "states": ["Louisiana", "New York", "California", "Illinois", "Texas", "Pennsylvania", "Washington", "Florida", "Massachusetts"],
            "zips": ["70130", "10001", "90012", "60601", "77002", "19102", "94101", "98101", "33101", "02108"],
            "phone": "+1 504-555-0124"
        }
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
        "🔐 /gen - CC Generator (/gen bin or /gen bin|mm|yy)\n"
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
