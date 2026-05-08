"""
╔══════════════════════════════════════════════════════════════╗
║        LEBONCOIN ARBITRAGE BOT — par ton assistant IA        ║
║  Détecte les bonnes affaires et alerte via Telegram          ║
╚══════════════════════════════════════════════════════════════╝

INSTALLATION :
  (déjà fait si tu as installé le bot Vinted)
  python -m pip install -r requirements.txt

CONFIGURATION :
  1. Crée un DEUXIÈME bot Telegram via @BotFather → copie le TOKEN
  2. Trouve ton CHAT_ID via @userinfobot
  3. Remplis la section CONFIG ci-dessous
  4. Lance : python leboncoin_bot.py
"""

import requests
import json
import time
import schedule
import os
from datetime import datetime
from colorama import Fore, Style, init
import asyncio
import telegram

init(autoreset=True)

# ═══════════════════════════════════════════════════════════════
#  ⚙️  CONFIG — REMPLIS CES VALEURS
# ═══════════════════════════════════════════════════════════════

TELEGRAM_TOKEN  = os.environ.get("TELEGRAM_TOKEN", "TON_TOKEN_ICI")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "TON_CHAT_ID_ICI")

CHECK_INTERVAL = 90   # secondes entre chaque vérification
MIN_MARGE      = 60   # % de plus-value minimum pour alerter

# ═══════════════════════════════════════════════════════════════
#  💎  BASE DE MARQUES & PRODUITS
# ═══════════════════════════════════════════════════════════════

MARQUES = {

    # ── MODE / STREETWEAR ──
    "stone island": {
        "prix_marche": 180, "categorie": "streetwear",
        "mots_cles": ["stone island", "stone_island"], "emoji": "🪨"
    },
    "supreme": {
        "prix_marche": 150, "categorie": "streetwear",
        "mots_cles": ["supreme"], "emoji": "🔴"
    },
    "palace": {
        "prix_marche": 120, "categorie": "streetwear",
        "mots_cles": ["palace"], "emoji": "🛹"
    },
    "off-white": {
        "prix_marche": 250, "categorie": "streetwear",
        "mots_cles": ["off white", "off-white", "offwhite"], "emoji": "⬜"
    },
    "cp company": {
        "prix_marche": 200, "categorie": "streetwear",
        "mots_cles": ["cp company", "c.p. company"], "emoji": "🔭"
    },
    "carhartt": {
        "prix_marche": 70, "categorie": "workwear",
        "mots_cles": ["carhartt"], "emoji": "🟧"
    },
    "ralph lauren": {
        "prix_marche": 100, "categorie": "premium",
        "mots_cles": ["ralph lauren", "polo ralph"], "emoji": "🏇"
    },
    "lacoste": {
        "prix_marche": 60, "categorie": "premium",
        "mots_cles": ["lacoste"], "emoji": "🐊"
    },
    "ami paris": {
        "prix_marche": 130, "categorie": "premium",
        "mots_cles": ["ami paris"], "emoji": "❤️"
    },

    # ── LUXE ──
    "gucci": {
        "prix_marche": 400, "categorie": "luxe",
        "mots_cles": ["gucci"], "emoji": "💚"
    },
    "louis vuitton": {
        "prix_marche": 600, "categorie": "luxe",
        "mots_cles": ["louis vuitton", "lv", "vuitton"], "emoji": "🟤"
    },
    "balenciaga": {
        "prix_marche": 350, "categorie": "luxe",
        "mots_cles": ["balenciaga"], "emoji": "⬛"
    },
    "moncler": {
        "prix_marche": 500, "categorie": "luxe",
        "mots_cles": ["moncler"], "emoji": "🏔️"
    },
    "canada goose": {
        "prix_marche": 400, "categorie": "luxe",
        "mots_cles": ["canada goose"], "emoji": "🦢"
    },
    "burberry": {
        "prix_marche": 280, "categorie": "luxe",
        "mots_cles": ["burberry"], "emoji": "🟨"
    },

    # ── SNEAKERS ──
    "jordan": {
        "prix_marche": 130, "categorie": "sneakers",
        "mots_cles": ["jordan", "air jordan", "aj1", "aj4"], "emoji": "🏀"
    },
    "yeezy": {
        "prix_marche": 200, "categorie": "sneakers",
        "mots_cles": ["yeezy"], "emoji": "🟤"
    },
    "new balance": {
        "prix_marche": 90, "categorie": "sneakers",
        "mots_cles": ["new balance", "nb 550", "nb 574", "990"], "emoji": "🔵"
    },
    "nike": {
        "prix_marche": 80, "categorie": "sneakers",
        "mots_cles": ["nike dunk", "air max", "air force 1"], "emoji": "✔️"
    },
    "adidas": {
        "prix_marche": 75, "categorie": "sneakers",
        "mots_cles": ["adidas samba", "adidas gazelle", "adidas campus"], "emoji": "⚫"
    },
    "salomon": {
        "prix_marche": 110, "categorie": "sneakers",
        "mots_cles": ["salomon xt", "salomon speedcross"], "emoji": "🏔️"
    },

    # ── VÉLOS ──
    "triban": {
        "prix_marche": 400, "categorie": "velo",
        "mots_cles": ["triban", "triban rc"], "emoji": "🚴"
    },
    "canyon": {
        "prix_marche": 800, "categorie": "velo",
        "mots_cles": ["canyon"], "emoji": "🏔️"
    },
    "trek": {
        "prix_marche": 700, "categorie": "velo",
        "mots_cles": ["trek"], "emoji": "🚵"
    },
    "specialized": {
        "prix_marche": 900, "categorie": "velo",
        "mots_cles": ["specialized"], "emoji": "⚡"
    },
    "btwin": {
        "prix_marche": 250, "categorie": "velo",
        "mots_cles": ["btwin", "b'twin"], "emoji": "🚲"
    },
    "giant": {
        "prix_marche": 600, "categorie": "velo",
        "mots_cles": ["giant"], "emoji": "🚴"
    },
    "scott": {
        "prix_marche": 700, "categorie": "velo",
        "mots_cles": ["scott velo", "scott bike"], "emoji": "🏁"
    },

    # ── ÉLECTRONIQUE ──
    "iphone": {
        "prix_marche": 600, "categorie": "electronique",
        "mots_cles": ["iphone 13", "iphone 14", "iphone 15", "iphone 16"], "emoji": "📱"
    },
    "macbook": {
        "prix_marche": 900, "categorie": "electronique",
        "mots_cles": ["macbook pro", "macbook air", "macbook m1", "macbook m2", "macbook m3"], "emoji": "💻"
    },
    "ipad": {
        "prix_marche": 400, "categorie": "electronique",
        "mots_cles": ["ipad pro", "ipad air", "ipad mini"], "emoji": "📟"
    },
    "airpods": {
        "prix_marche": 150, "categorie": "electronique",
        "mots_cles": ["airpods pro", "airpods max"], "emoji": "🎧"
    },
    "apple watch": {
        "prix_marche": 250, "categorie": "electronique",
        "mots_cles": ["apple watch", "apple watch ultra", "apple watch series"], "emoji": "⌚"
    },
    "sony playstation": {
        "prix_marche": 400, "categorie": "electronique",
        "mots_cles": ["ps5", "playstation 5"], "emoji": "🎮"
    },
    "sony ps4": {
        "prix_marche": 180, "categorie": "electronique",
        "mots_cles": ["ps4", "playstation 4"], "emoji": "🎮"
    },
    "sony camera": {
        "prix_marche": 700, "categorie": "electronique",
        "mots_cles": ["sony a7", "sony zv", "sony alpha"], "emoji": "📷"
    },
    "sony headphones": {
        "prix_marche": 200, "categorie": "electronique",
        "mots_cles": ["sony wh-1000", "sony wf-1000"], "emoji": "🎧"
    },
    "samsung galaxy": {
        "prix_marche": 500, "categorie": "electronique",
        "mots_cles": ["samsung s23", "samsung s24", "samsung s25", "galaxy s"], "emoji": "📱"
    },
    "nintendo switch": {
        "prix_marche": 220, "categorie": "electronique",
        "mots_cles": ["nintendo switch", "switch oled"], "emoji": "🎮"
    },
    "xbox": {
        "prix_marche": 350, "categorie": "electronique",
        "mots_cles": ["xbox series x", "xbox series s"], "emoji": "🎮"
    },
    "gopro": {
        "prix_marche": 250, "categorie": "electronique",
        "mots_cles": ["gopro hero", "gopro 10", "gopro 11", "gopro 12"], "emoji": "📹"
    },
    "dyson": {
        "prix_marche": 300, "categorie": "electronique",
        "mots_cles": ["dyson airwrap", "dyson v11", "dyson v12", "dyson v15"], "emoji": "🌀"
    },

    # ── MONTRES & BIJOUX ──
    "rolex": {
        "prix_marche": 8000, "categorie": "montre",
        "mots_cles": ["rolex"], "emoji": "⌚"
    },
    "omega": {
        "prix_marche": 3000, "categorie": "montre",
        "mots_cles": ["omega seamaster", "omega speedmaster"], "emoji": "⌚"
    },
    "tag heuer": {
        "prix_marche": 1500, "categorie": "montre",
        "mots_cles": ["tag heuer", "tagheuer"], "emoji": "⌚"
    },
    "casio g-shock": {
        "prix_marche": 150, "categorie": "montre",
        "mots_cles": ["g-shock", "gshock", "casio gw"], "emoji": "⌚"
    },
    "bracelet gold": {
        "prix_marche": 200, "categorie": "bijou",
        "mots_cles": ["bracelet or 18k", "bracelet or 14k", "bracelet plaqué or"], "emoji": "📿"
    },
    "collier or": {
        "prix_marche": 300, "categorie": "bijou",
        "mots_cles": ["collier or", "chaine or 18k"], "emoji": "📿"
    },
}

# ═══════════════════════════════════════════════════════════════
#  🔍  RECHERCHES LEBONCOIN
# ═══════════════════════════════════════════════════════════════

RECHERCHES = [
    {
        "nom": "Vestes & Manteaux premium",
        "params": {
            "category": "11",        # Mode homme
            "locations": "",
            "price_min": "1",
            "price_max": "200",
            "sort": "time",
            "order": "desc",
        },
        "keywords": "veste manteau stone island supreme palace moncler canada goose"
    },
    {
        "nom": "Streetwear marques",
        "params": {
            "category": "11",
            "price_max": "300",
            "sort": "time",
            "order": "desc",
        },
        "keywords": "stone island supreme palace off white balenciaga gucci"
    },
    {
        "nom": "Sneakers hype",
        "params": {
            "category": "11",
            "price_max": "200",
            "sort": "time",
            "order": "desc",
        },
        "keywords": "jordan yeezy dunk new balance salomon"
    },
    {
        "nom": "Vélos Triban & marques",
        "params": {
            "category": "36",        # Vélos
            "price_min": "50",
            "price_max": "1500",
            "sort": "time",
            "order": "desc",
        },
        "keywords": "triban canyon trek specialized giant scott"
    },
    {
        "nom": "iPhone & Apple",
        "params": {
            "category": "15",        # Téléphones
            "price_min": "50",
            "price_max": "800",
            "sort": "time",
            "order": "desc",
        },
        "keywords": "iphone 13 14 15 16 macbook airpods apple watch"
    },
    {
        "nom": "PlayStation & Gaming",
        "params": {
            "category": "142",       # Consoles & jeux
            "price_min": "50",
            "price_max": "500",
            "sort": "time",
            "order": "desc",
        },
        "keywords": "ps5 playstation 5 xbox series nintendo switch"
    },
    {
        "nom": "Sony & Électronique",
        "params": {
            "category": "15",
            "price_min": "30",
            "price_max": "1000",
            "sort": "time",
            "order": "desc",
        },
        "keywords": "sony samsung dyson gopro"
    },
    {
        "nom": "Montres & Bijoux",
        "params": {
            "category": "245",       # Montres & bijoux
            "price_min": "30",
            "price_max": "5000",
            "sort": "time",
            "order": "desc",
        },
        "keywords": "rolex omega tag heuer g-shock bracelet collier or"
    },
]

# ═══════════════════════════════════════════════════════════════
#  💾  STOCKAGE
# ═══════════════════════════════════════════════════════════════

SEEN_FILE = "leboncoin_seen.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

seen_ids = load_seen()

# ═══════════════════════════════════════════════════════════════
#  🌐  SCRAPER LEBONCOIN
# ═══════════════════════════════════════════════════════════════

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Referer": "https://www.leboncoin.fr/",
    "api_key": "ba0c2dad52b3565c9a1b4d0e9af05d65",  # Clé publique Leboncoin
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def search_leboncoin(recherche):
    """Appelle l'API Leboncoin"""
    try:
        # Construction du body de recherche
        body = {
            "filters": {
                "category": {"id": recherche["params"].get("category", "")},
                "keywords": {"text": recherche["keywords"]},
                "ranges": {}
            },
            "sort_by": "time",
            "sort_order": "desc",
            "limit": 100,
            "offset": 0,
        }

        # Ajouter les filtres de prix
        if recherche["params"].get("price_max"):
            body["filters"]["ranges"]["price"] = {
                "max": int(recherche["params"]["price_max"])
            }
        if recherche["params"].get("price_min"):
            if "price" not in body["filters"]["ranges"]:
                body["filters"]["ranges"]["price"] = {}
            body["filters"]["ranges"]["price"]["min"] = int(recherche["params"]["price_min"])

        r = SESSION.post(
            "https://api.leboncoin.fr/api/adfinder/v1/search",
            json=body,
            timeout=15
        )

        if r.status_code == 200:
            data = r.json()
            return data.get("ads", [])
        else:
            print(f"{Fore.YELLOW}⚠️ Status {r.status_code} pour {recherche['nom']}")
            return []

    except Exception as e:
        print(f"{Fore.RED}❌ Erreur API Leboncoin: {e}")
        return []

# ═══════════════════════════════════════════════════════════════
#  📊  ANALYSE DE LA PLUS-VALUE
# ═══════════════════════════════════════════════════════════════

def detecter_marque(titre, description=""):
    texte = (titre + " " + description).lower()
    meilleure_marque = None
    meilleur_score = 0

    for nom_marque, info in MARQUES.items():
        for mot_cle in info["mots_cles"]:
            if mot_cle in texte:
                score = len(mot_cle)
                if score > meilleur_score:
                    meilleur_score = score
                    meilleure_marque = (nom_marque, info)

    return meilleure_marque

def calculer_marge(prix, prix_marche):
    if prix <= 0:
        return 0
    return round(((prix_marche - prix) / prix) * 100, 1)

def analyser_article(ad):
    try:
        ad_id   = str(ad.get("list_id", ""))
        titre   = ad.get("subject", "")
        prix    = float(ad.get("price", [0])[0] if isinstance(ad.get("price"), list) else ad.get("price", 0))
        url     = ad.get("url", f"https://www.leboncoin.fr/annonces/{ad_id}")
        desc    = ad.get("body", "")
        ville   = ad.get("location", {}).get("city", "?")

        # Photo
        images  = ad.get("images", {})
        photos  = images.get("urls_large", images.get("urls", []))
        photo   = photos[0] if photos else ""

        resultat = detecter_marque(titre, desc)
        if not resultat:
            return None

        nom_marque, info_marque = resultat
        prix_marche = info_marque["prix_marche"]
        marge = calculer_marge(prix, prix_marche)

        if marge >= MIN_MARGE:
            return {
                "id": ad_id,
                "titre": titre,
                "prix": prix,
                "marque": nom_marque,
                "emoji_marque": info_marque["emoji"],
                "categorie": info_marque["categorie"],
                "prix_marche": prix_marche,
                "marge": marge,
                "ville": ville,
                "url": url,
                "photo": photo,
            }
    except Exception as e:
        pass
    return None

# ═══════════════════════════════════════════════════════════════
#  📱  TELEGRAM
# ═══════════════════════════════════════════════════════════════

async def send_telegram_alert(affaire):
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)

        if affaire["marge"] >= 200:
            niveau = "🚨 DEAL EXCEPTIONNEL"
            urgence = "⚡⚡⚡"
        elif affaire["marge"] >= 100:
            niveau = "🔥 TRÈS BONNE AFFAIRE"
            urgence = "⚡⚡"
        else:
            niveau = "✅ BONNE AFFAIRE"
            urgence = "⚡"

        prix_revente = round(affaire["prix_marche"] * 0.75)
        profit = round(prix_revente - affaire["prix"])

        msg = f"""
{urgence} *{niveau}* {urgence}
🏷️ *LEBONCOIN*

{affaire["emoji_marque"]} *{affaire["marque"].upper()}*
📦 {affaire["titre"]}

💰 *Prix annonce :* {affaire["prix"]}€
🏷️ *Prix marché :* ~{affaire["prix_marche"]}€
📈 *Plus-value :* +{affaire["marge"]}%
💵 *Revendre ~{prix_revente}€ → profit ~{profit}€*

📍 Ville : {affaire["ville"]}
🗂️ Catégorie : {affaire["categorie"]}

🔗 [VOIR L'ANNONCE]({affaire["url"]})
"""
        if affaire["photo"]:
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=affaire["photo"],
                caption=msg,
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=msg,
                parse_mode="Markdown"
            )
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur Telegram: {e}")
        return False

def send_alert(affaire):
    asyncio.run(send_telegram_alert(affaire))

async def send_startup_message():
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"🤖 *Leboncoin Arbitrage Bot démarré !*\n\n"
                 f"🔍 {len(RECHERCHES)} recherches actives\n"
                 f"💎 {len(MARQUES)} marques/produits surveillés\n"
                 f"📊 Alerte si plus-value ≥ {MIN_MARGE}%\n"
                 f"⏱️ Vérification toutes les {CHECK_INTERVAL}s\n\n"
                 f"_Catégories : Mode, Vélos, Électronique, Montres & Bijoux_",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur message démarrage: {e}")

# ═══════════════════════════════════════════════════════════════
#  🔄  BOUCLE PRINCIPALE
# ═══════════════════════════════════════════════════════════════

def check_leboncoin():
    global seen_ids
    now = datetime.now().strftime("%H:%M:%S")
    total_deals = 0
    total_new = 0

    print(f"\n{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"{Fore.CYAN}🔍 [{now}] Vérification Leboncoin...")

    for recherche in RECHERCHES:
        print(f"{Fore.WHITE}  → {recherche['nom']}...")
        ads = search_leboncoin(recherche)

        nouveaux = 0
        deals = 0

        for ad in ads:
            ad_id = str(ad.get("list_id", ""))
            if ad_id in seen_ids:
                continue

            seen_ids.add(ad_id)
            nouveaux += 1

            affaire = analyser_article(ad)
            if affaire:
                deals += 1
                total_deals += 1
                print(f"\n{Fore.GREEN}  🔥 DEAL TROUVÉ !")
                print(f"  {affaire['emoji_marque']} {affaire['marque'].upper()} — {affaire['titre'][:50]}")
                print(f"  💰 {affaire['prix']}€ | Marché: {affaire['prix_marche']}€ | +{affaire['marge']}%")
                print(f"  📍 {affaire['ville']} | 🔗 {affaire['url']}")
                send_alert(affaire)

        total_new += nouveaux
        if nouveaux > 0:
            print(f"{Fore.WHITE}    ✓ {nouveaux} nouvelles annonces, {deals} deals")

        time.sleep(3)  # Pause entre requêtes

    save_seen(seen_ids)

    if total_deals == 0:
        print(f"{Fore.YELLOW}  Aucun deal. {total_new} nouvelles annonces analysées.")
    else:
        print(f"\n{Fore.GREEN}✅ {total_deals} deal(s) envoyé(s) sur Telegram !")

# ═══════════════════════════════════════════════════════════════
#  🚀  LANCEMENT
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"""
{Fore.YELLOW}╔══════════════════════════════════════════════════╗
║     🏷️  LEBONCOIN ARBITRAGE BOT  🏷️              ║
║   Mode · Vélos · Électronique · Montres          ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.WHITE}Config:
  • Marges ciblées    : +{MIN_MARGE}% minimum
  • Marques surveillées: {len(MARQUES)}
  • Recherches actives : {len(RECHERCHES)}
  • Intervalle         : {CHECK_INTERVAL}s
""")

    if "TON_TOKEN" in TELEGRAM_TOKEN or "TON_CHAT" in TELEGRAM_CHAT_ID:
        print(f"{Fore.RED}⚠️  Configure TELEGRAM_TOKEN et TELEGRAM_CHAT_ID !")
        input("Appuie sur Entrée pour continuer sans Telegram...")
    else:
        asyncio.run(send_startup_message())

    check_leboncoin()
    schedule.every(CHECK_INTERVAL).seconds.do(check_leboncoin)

    print(f"\n{Fore.GREEN}✅ Bot lancé ! Vérification toutes les {CHECK_INTERVAL}s.")
    print(f"{Fore.WHITE}   Ctrl+C pour arrêter.\n")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
