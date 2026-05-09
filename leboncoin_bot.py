"""
LEBONCOIN RSS BOT
"""
import requests, json, time, schedule, os, re
import xml.etree.ElementTree as ET
from datetime import datetime
from colorama import Fore, Style, init
import asyncio, telegram

init(autoreset=True)

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "TON_TOKEN_ICI")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "TON_CHAT_ID_ICI")
CHECK_INTERVAL = 120
MIN_MARGE = 60

MARQUES = {
    "stone island":  {"prix_marche": 180, "mots_cles": ["stone island"], "emoji": "🪨"},
    "supreme":       {"prix_marche": 150, "mots_cles": ["supreme"], "emoji": "🔴"},
    "palace":        {"prix_marche": 120, "mots_cles": ["palace"], "emoji": "🛹"},
    "off-white":     {"prix_marche": 250, "mots_cles": ["off white", "off-white"], "emoji": "⬜"},
    "cp company":    {"prix_marche": 200, "mots_cles": ["cp company"], "emoji": "🔭"},
    "carhartt":      {"prix_marche": 70,  "mots_cles": ["carhartt"], "emoji": "🟧"},
    "ralph lauren":  {"prix_marche": 100, "mots_cles": ["ralph lauren", "polo ralph"], "emoji": "🏇"},
    "lacoste":       {"prix_marche": 60,  "mots_cles": ["lacoste"], "emoji": "🐊"},
    "gucci":         {"prix_marche": 400, "mots_cles": ["gucci"], "emoji": "💚"},
    "louis vuitton": {"prix_marche": 600, "mots_cles": ["louis vuitton", "vuitton"], "emoji": "🟤"},
    "balenciaga":    {"prix_marche": 350, "mots_cles": ["balenciaga"], "emoji": "⬛"},
    "moncler":       {"prix_marche": 500, "mots_cles": ["moncler"], "emoji": "🏔️"},
    "canada goose":  {"prix_marche": 400, "mots_cles": ["canada goose"], "emoji": "🦢"},
    "burberry":      {"prix_marche": 280, "mots_cles": ["burberry"], "emoji": "🟨"},
    "jordan":        {"prix_marche": 130, "mots_cles": ["jordan", "air jordan"], "emoji": "🏀"},
    "yeezy":         {"prix_marche": 200, "mots_cles": ["yeezy"], "emoji": "🟤"},
    "new balance":   {"prix_marche": 90,  "mots_cles": ["new balance", "nb 550", "990"], "emoji": "🔵"},
    "nike dunk":     {"prix_marche": 100, "mots_cles": ["nike dunk", "air force 1", "air max"], "emoji": "✔️"},
    "salomon":       {"prix_marche": 110, "mots_cles": ["salomon xt", "salomon speedcross"], "emoji": "🏔️"},
    "triban":        {"prix_marche": 400, "mots_cles": ["triban"], "emoji": "🚴"},
    "canyon":        {"prix_marche": 800, "mots_cles": ["canyon"], "emoji": "🏔️"},
    "trek":          {"prix_marche": 700, "mots_cles": ["trek"], "emoji": "🚵"},
    "specialized":   {"prix_marche": 900, "mots_cles": ["specialized"], "emoji": "⚡"},
    "iphone":        {"prix_marche": 600, "mots_cles": ["iphone 13", "iphone 14", "iphone 15", "iphone 16"], "emoji": "📱"},
    "macbook":       {"prix_marche": 900, "mots_cles": ["macbook pro", "macbook air", "macbook m1", "macbook m2"], "emoji": "💻"},
    "airpods":       {"prix_marche": 150, "mots_cles": ["airpods pro", "airpods max"], "emoji": "🎧"},
    "apple watch":   {"prix_marche": 250, "mots_cles": ["apple watch"], "emoji": "⌚"},
    "ps5":           {"prix_marche": 400, "mots_cles": ["ps5", "playstation 5"], "emoji": "🎮"},
    "ps4":           {"prix_marche": 180, "mots_cles": ["ps4", "playstation 4"], "emoji": "🎮"},
    "nintendo":      {"prix_marche": 220, "mots_cles": ["nintendo switch", "switch oled"], "emoji": "🎮"},
    "xbox":          {"prix_marche": 350, "mots_cles": ["xbox series"], "emoji": "🎮"},
    "gopro":         {"prix_marche": 250, "mots_cles": ["gopro hero"], "emoji": "📹"},
    "dyson":         {"prix_marche": 300, "mots_cles": ["dyson airwrap", "dyson v11", "dyson v12", "dyson v15"], "emoji": "🌀"},
    "rolex":         {"prix_marche": 8000,"mots_cles": ["rolex"], "emoji": "⌚"},
    "omega":         {"prix_marche": 3000,"mots_cles": ["omega seamaster", "omega speedmaster"], "emoji": "⌚"},
    "tag heuer":     {"prix_marche": 1500,"mots_cles": ["tag heuer"], "emoji": "⌚"},
    "g-shock":       {"prix_marche": 150, "mots_cles": ["g-shock", "gshock"], "emoji": "⌚"},
}

FLUX_RSS = [
    {"nom": "Stone Island / Supreme", "url": "https://www.leboncoin.fr/recherche.rss?text=stone+island+supreme+palace&category=11"},
    {"nom": "Luxe mode", "url": "https://www.leboncoin.fr/recherche.rss?text=moncler+balenciaga+gucci+vuitton&category=11"},
    {"nom": "Sneakers hype", "url": "https://www.leboncoin.fr/recherche.rss?text=jordan+yeezy+dunk+new+balance&category=11"},
    {"nom": "Vélos", "url": "https://www.leboncoin.fr/recherche.rss?text=triban+canyon+trek+specialized&category=36"},
    {"nom": "iPhone Apple", "url": "https://www.leboncoin.fr/recherche.rss?text=iphone+macbook+airpods&category=15"},
    {"nom": "Gaming", "url": "https://www.leboncoin.fr/recherche.rss?text=ps5+xbox+nintendo+switch&category=142"},
    {"nom": "Sony Samsung Dyson", "url": "https://www.leboncoin.fr/recherche.rss?text=sony+samsung+dyson+gopro"},
    {"nom": "Montres bijoux", "url": "https://www.leboncoin.fr/recherche.rss?text=rolex+omega+tag+heuer+bracelet+or&category=245"},
]

SEEN_FILE = "leboncoin_rss_seen.json"

def load_seen():
    try:
        if os.path.exists(SEEN_FILE):
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
    except:
        pass
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen)[-5000:], f)

seen_ids = load_seen()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

def fetch_rss(flux):
    try:
        r = requests.get(flux["url"], headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall(".//item"):
            titre = item.findtext("title", "")
            lien  = item.findtext("link", "")
            desc  = item.findtext("description", "")
            guid  = item.findtext("guid", lien)
            prix  = extraire_prix(titre + " " + desc)
            items.append({"id": guid, "titre": titre, "prix": prix, "url": lien, "description": desc})
        return items
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur RSS {flux['nom']}: {e}")
        return []

def extraire_prix(texte):
    for pattern in [r'(\d+[\s]?\d*)\s*€', r'(\d+)\s*euros?']:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(' ', ''))
            except:
                pass
    return 0

def detecter_marque(titre, desc=""):
    texte = (titre + " " + desc).lower()
    best = None
    best_score = 0
    for nom, info in MARQUES.items():
        for mot in info["mots_cles"]:
            if mot in texte and len(mot) > best_score:
                best_score = len(mot)
                best = (nom, info)
    return best

def analyser_item(item):
    if not item["prix"] or item["prix"] <= 0:
        return None
    resultat = detecter_marque(item["titre"], item["description"])
    if not resultat:
        return None
    nom, info = resultat
    marge = round(((info["prix_marche"] - item["prix"]) / item["prix"]) * 100, 1)
    if marge >= MIN_MARGE:
        return {**item, "marque": nom, "emoji": info["emoji"], "prix_marche": info["prix_marche"], "marge": marge}
    return None

async def send_alert_async(a):
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        urgence = "⚡⚡⚡" if a["marge"] >= 200 else "⚡⚡" if a["marge"] >= 100 else "⚡"
        niveau  = "🚨 DEAL EXCEPTIONNEL" if a["marge"] >= 200 else "🔥 TRÈS BONNE AFFAIRE" if a["marge"] >= 100 else "✅ BONNE AFFAIRE"
        revente = round(a["prix_marche"] * 0.75)
        profit  = round(revente - a["prix"])
        msg = f"""{urgence} *{niveau}* {urgence}
🏷️ *LEBONCOIN*

{a["emoji"]} *{a["marque"].upper()}*
📦 {a["titre"]}

💰 *Prix :* {a["prix"]}€
🏷️ *Marché :* ~{a["prix_marche"]}€
📈 *Plus-value :* +{a["marge"]}%
💵 *Revendre ~{revente}€ → profit ~{profit}€*

🔗 [VOIR L'ANNONCE]({a["url"]})"""
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode="Markdown")
    except Exception as e:
        print(f"{Fore.RED}❌ Telegram: {e}")

def send_alert(a):
    asyncio.run(send_alert_async(a))

def check_leboncoin():
    global seen_ids
    now = datetime.now().strftime("%H:%M:%S")
    total = 0
    print(f"\n{Fore.YELLOW}🔍 [{now}] Scan Leboncoin RSS...")
    for flux in FLUX_RSS:
        print(f"  → {flux['nom']}...")
        items = fetch_rss(flux)
        for item in items:
            if item["id"] in seen_ids:
                continue
            seen_ids.add(item["id"])
            affaire = analyser_item(item)
            if affaire:
                total += 1
                print(f"{Fore.GREEN}  🔥 {affaire['marque'].upper()} — {affaire['prix']}€ | +{affaire['marge']}%")
                send_alert(affaire)
        time.sleep(2)
    save_seen(seen_ids)
    if total == 0:
        print(f"{Fore.YELLOW}  Aucun deal cette fois.")
    else:
        print(f"{Fore.GREEN}✅ {total} deal(s) envoyés !")

def main():
    print(f"{Fore.YELLOW}🏷️ LEBONCOIN RSS BOT démarré !{Style.RESET_ALL}")
    try:
        asyncio.run(telegram.Bot(token=TELEGRAM_TOKEN).send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"🏷️ *Leboncoin RSS Bot démarré !*\n\n🔍 {len(FLUX_RSS)} flux RSS\n💎 {len(MARQUES)} marques\n📊 Alerte si +{MIN_MARGE}%\n⏱️ Toutes les {CHECK_INTERVAL}s",
            parse_mode="Markdown"
        ))
    except Exception as e:
        print(f"Erreur démarrage: {e}")
    check_leboncoin()
    schedule.every(CHECK_INTERVAL).seconds.do(check_leboncoin)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
