"""
╔══════════════════════════════════════════════════════════════╗
║          VINTED ARBITRAGE BOT — par ton assistant IA         ║
║  Détecte les bonnes affaires et alerte via Telegram          ║
╚══════════════════════════════════════════════════════════════╝

INSTALLATION :
  pip install requests python-telegram-bot schedule colorama

CONFIGURATION :
  1. Crée un bot Telegram via @BotFather → copie le TOKEN
  2. Trouve ton CHAT_ID via @userinfobot
  3. Remplis la section CONFIG ci-dessous
  4. Lance : python vinted_bot.py
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

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "TON_TOKEN_ICI")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "TON_CHAT_ID_ICI")

# Intervalle de vérification (en secondes)
CHECK_INTERVAL = 60  # Vérifie toutes les 60 secondes

# Plus-value minimale pour alerter (en %)
MIN_MARGE = 60

# ═══════════════════════════════════════════════════════════════
#  💎  BASE DE MARQUES — Prix marché de revente estimé (€)
#  (Prix moyen de revente sur Vinted/Vestiaire en bon état)
# ═══════════════════════════════════════════════════════════════

MARQUES = {
    # ── STREETWEAR / HYPE ──
    "stone island": {
        "prix_marche": 180, "categorie": "streetwear",
        "mots_cles": ["stone island", "stone_island"],
        "emoji": "🪨"
    },
    "palace": {
        "prix_marche": 120, "categorie": "streetwear",
        "mots_cles": ["palace"],
        "emoji": "🛹"
    },
    "supreme": {
        "prix_marche": 150, "categorie": "streetwear",
        "mots_cles": ["supreme"],
        "emoji": "🔴"
    },
    "off-white": {
        "prix_marche": 250, "categorie": "streetwear",
        "mots_cles": ["off white", "off-white", "offwhite", "virgil"],
        "emoji": "⬜"
    },
    "kith": {
        "prix_marche": 130, "categorie": "streetwear",
        "mots_cles": ["kith"],
        "emoji": "🏙️"
    },
    "apc": {
        "prix_marche": 100, "categorie": "streetwear",
        "mots_cles": ["a.p.c", "apc"],
        "emoji": "🇫🇷"
    },
    "ami paris": {
        "prix_marche": 130, "categorie": "streetwear",
        "mots_cles": ["ami paris", "ami alexandre mattiussi"],
        "emoji": "❤️"
    },

    # ── SNEAKERS / CHAUSSURES ──
    "nike": {
        "prix_marche": 80, "categorie": "sneakers",
        "mots_cles": ["nike", "air max", "air force", "dunk", "jordan"],
        "emoji": "✔️"
    },
    "jordan": {
        "prix_marche": 130, "categorie": "sneakers",
        "mots_cles": ["jordan", "air jordan", "aj1", "aj4"],
        "emoji": "🏀"
    },
    "new balance": {
        "prix_marche": 90, "categorie": "sneakers",
        "mots_cles": ["new balance", "newbalance", "nb 550", "nb 574", "990"],
        "emoji": "🔵"
    },
    "adidas": {
        "prix_marche": 75, "categorie": "sneakers",
        "mots_cles": ["adidas", "yeezy", "gazelle", "samba", "campus"],
        "emoji": "⚫"
    },
    "yeezy": {
        "prix_marche": 200, "categorie": "sneakers",
        "mots_cles": ["yeezy", "yeezys"],
        "emoji": "🟤"
    },
    "salomon": {
        "prix_marche": 110, "categorie": "sneakers",
        "mots_cles": ["salomon", "xt-6", "xt6", "speedcross"],
        "emoji": "🏔️"
    },

    # ── VESTES / MANTEAUX ──
    "moncler": {
        "prix_marche": 500, "categorie": "luxe",
        "mots_cles": ["moncler"],
        "emoji": "🏔️"
    },
    "canada goose": {
        "prix_marche": 400, "categorie": "luxe",
        "mots_cles": ["canada goose", "canada_goose"],
        "emoji": "🦢"
    },
    "the north face": {
        "prix_marche": 150, "categorie": "outdoor",
        "mots_cles": ["north face", "northface", "tnf", "nuptse"],
        "emoji": "⛺"
    },
    "arc'teryx": {
        "prix_marche": 300, "categorie": "outdoor",
        "mots_cles": ["arcteryx", "arc'teryx", "arc teryx"],
        "emoji": "🦅"
    },

    # ── LUXE ──
    "gucci": {
        "prix_marche": 400, "categorie": "luxe",
        "mots_cles": ["gucci"],
        "emoji": "💚"
    },
    "louis vuitton": {
        "prix_marche": 600, "categorie": "luxe",
        "mots_cles": ["louis vuitton", "lv", "l.v", "vuitton"],
        "emoji": "🟤"
    },
    "balenciaga": {
        "prix_marche": 350, "categorie": "luxe",
        "mots_cles": ["balenciaga", "balencia"],
        "emoji": "⬛"
    },
    "burberry": {
        "prix_marche": 280, "categorie": "luxe",
        "mots_cles": ["burberry"],
        "emoji": "🟨"
    },
    "ralph lauren": {
        "prix_marche": 100, "categorie": "premium",
        "mots_cles": ["ralph lauren", "polo ralph", "polo rl"],
        "emoji": "🏇"
    },
    "lacoste": {
        "prix_marche": 60, "categorie": "premium",
        "mots_cles": ["lacoste"],
        "emoji": "🐊"
    },
    "cp company": {
        "prix_marche": 200, "categorie": "streetwear",
        "mots_cles": ["cp company", "c.p. company", "cpcompany"],
        "emoji": "🔭"
    },
    "carhartt": {
        "prix_marche": 70, "categorie": "workwear",
        "mots_cles": ["carhartt", "carhart"],
        "emoji": "🟧"
    },
    "levi's": {
        "prix_marche": 50, "categorie": "denim",
        "mots_cles": ["levis", "levi's", "levi strauss"],
        "emoji": "👖"
    },
}

# ═══════════════════════════════════════════════════════════════
#  🔍  RECHERCHES VINTED — Personnalise tes recherches
# ═══════════════════════════════════════════════════════════════

RECHERCHES = [
    {
        "nom": "Vestes & Manteaux premium",
        "params": {
            "search_text": "",
            "catalog_ids": "1",        # 1 = Hommes
            "category_ids": "1037",    # Vestes & Manteaux
            "price_to": "150",         # Max 150€
            "order": "newest_first",
            "per_page": "96",
        }
    },
    {
        "nom": "Streetwear marques",
        "params": {
            "search_text": "stone island palace supreme kith",
            "catalog_ids": "1",
            "price_to": "200",
            "order": "newest_first",
            "per_page": "96",
        }
    },
    {
        "nom": "Sneakers hype",
        "params": {
            "search_text": "jordan yeezy dunk",
            "catalog_ids": "1",
            "category_ids": "305",     # Chaussures
            "price_to": "150",
            "order": "newest_first",
            "per_page": "96",
        }
    },
    {
        "nom": "Luxe pas cher",
        "params": {
            "search_text": "gucci balenciaga burberry moncler",
            "price_to": "300",
            "order": "newest_first",
            "per_page": "96",
        }
    },
]

# ═══════════════════════════════════════════════════════════════
#  💾  STOCKAGE des annonces déjà vues
# ═══════════════════════════════════════════════════════════════

SEEN_FILE = "vinted_seen.json"

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
#  🌐  SCRAPER VINTED
# ═══════════════════════════════════════════════════════════════

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Referer": "https://www.vinted.fr/",
    "Origin": "https://www.vinted.fr",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def get_vinted_token():
    """Récupère le cookie CSRF de Vinted"""
    try:
        r = SESSION.get("https://www.vinted.fr", timeout=10)
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur connexion Vinted: {e}")
        return False

def search_vinted(params):
    """Appelle l'API Vinted"""
    try:
        url = "https://www.vinted.fr/api/v2/catalog/items"
        r = SESSION.get(url, params=params, timeout=15)
        
        if r.status_code == 401:
            get_vinted_token()
            r = SESSION.get(url, params=params, timeout=15)
        
        if r.status_code == 200:
            return r.json().get("items", [])
        else:
            print(f"{Fore.YELLOW}⚠️ Status {r.status_code}")
            return []
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur API: {e}")
        return []

# ═══════════════════════════════════════════════════════════════
#  📊  ANALYSE DE LA PLUS-VALUE
# ═══════════════════════════════════════════════════════════════

def detecter_marque(titre, description=""):
    """Détecte la marque dans le titre/description"""
    texte = (titre + " " + description).lower()
    
    meilleure_marque = None
    meilleur_score = 0
    
    for nom_marque, info in MARQUES.items():
        for mot_cle in info["mots_cles"]:
            if mot_cle in texte:
                # Score basé sur la longueur du mot-clé (plus précis = mieux)
                score = len(mot_cle)
                if score > meilleur_score:
                    meilleur_score = score
                    meilleure_marque = (nom_marque, info)
    
    return meilleure_marque

def calculer_marge(prix_vinted, prix_marche):
    """
    Calcule la plus-value potentielle
    Si prix_vinted = 50€ et prix_marche = 150€
    → tu peux revendre à 150€ → plus-value de 200%
    → ou revendre à 120€ → plus-value de 140%
    """
    if prix_vinted <= 0:
        return 0
    marge = ((prix_marche - prix_vinted) / prix_vinted) * 100
    return round(marge, 1)

def analyser_article(item):
    """Analyse un article et retourne les infos si bonne affaire"""
    try:
        item_id = str(item.get("id", ""))
        titre = item.get("title", "")
        prix = float(item.get("price", {}).get("amount", 0) if isinstance(item.get("price"), dict) else item.get("price", 0))
        url = f"https://www.vinted.fr/items/{item_id}"
        
        # Photo
        photos = item.get("photos", [])
        photo_url = photos[0].get("full_size_url", "") if photos else ""
        
        # Taille & état
        taille = item.get("size_title", "?")
        etat = item.get("status", "")
        
        # Détecter la marque
        brand = item.get("brand_title", "") or ""
        resultat = detecter_marque(titre + " " + brand)
        
        if not resultat:
            return None
        
        nom_marque, info_marque = resultat
        prix_marche = info_marque["prix_marche"]
        marge = calculer_marge(prix, prix_marche)
        
        if marge >= MIN_MARGE:
            return {
                "id": item_id,
                "titre": titre,
                "prix": prix,
                "marque": nom_marque,
                "emoji_marque": info_marque["emoji"],
                "categorie": info_marque["categorie"],
                "prix_marche": prix_marche,
                "marge": marge,
                "taille": taille,
                "etat": etat,
                "url": url,
                "photo": photo_url,
                "vendeur": item.get("user", {}).get("login", "?"),
            }
    except Exception as e:
        pass
    return None

# ═══════════════════════════════════════════════════════════════
#  📱  TELEGRAM
# ═══════════════════════════════════════════════════════════════

async def send_telegram_alert(affaire):
    """Envoie une alerte Telegram avec photo"""
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        
        # Niveau d'alerte
        if affaire["marge"] >= 200:
            niveau = "🚨 DEAL EXCEPTIONNEL"
            urgence = "⚡⚡⚡"
        elif affaire["marge"] >= 100:
            niveau = "🔥 TRÈS BONNE AFFAIRE"
            urgence = "⚡⚡"
        else:
            niveau = "✅ BONNE AFFAIRE"
            urgence = "⚡"
        
        # Prix de revente conseillé
        prix_revente_conseille = round(affaire["prix_marche"] * 0.75)
        profit_estime = prix_revente_conseille - affaire["prix"] - (affaire["prix"] * 0.05)  # -5% frais Vinted
        
        msg = f"""
{urgence} *{niveau}* {urgence}

{affaire["emoji_marque"]} *{affaire["marque"].upper()}*
📦 {affaire["titre"]}

💰 *Prix Vinted :* {affaire["prix"]}€
🏷️ *Prix marché :* ~{affaire["prix_marche"]}€
📈 *Plus-value potentielle :* +{affaire["marge"]}%
💵 *Revendre à ~{prix_revente_conseille}€ → profit ~{profit_estime:.0f}€*

📏 Taille : {affaire["taille"]}
🏪 Vendeur : {affaire["vendeur"]}
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
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
        
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur Telegram: {e}")
        return False

def send_alert(affaire):
    asyncio.run(send_telegram_alert(affaire))

async def send_startup_message():
    """Message de démarrage"""
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"🤖 *Vinted Arbitrage Bot démarré !*\n\n"
                 f"🔍 Je surveille {len(RECHERCHES)} recherches\n"
                 f"💎 {len(MARQUES)} marques en base\n"
                 f"📊 Alerte si plus-value ≥ {MIN_MARGE}%\n"
                 f"⏱️ Vérification toutes les {CHECK_INTERVAL}s\n\n"
                 f"_Je t'envoie un message dès que je trouve une bonne affaire !_",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur message démarrage: {e}")

# ═══════════════════════════════════════════════════════════════
#  🔄  BOUCLE PRINCIPALE
# ═══════════════════════════════════════════════════════════════

def check_vinted():
    """Vérifie toutes les recherches Vinted"""
    global seen_ids
    now = datetime.now().strftime("%H:%M:%S")
    total_new = 0
    total_deals = 0
    
    print(f"\n{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"{Fore.CYAN}🔍 [{now}] Vérification en cours...")
    
    for recherche in RECHERCHES:
        print(f"{Fore.WHITE}  → {recherche['nom']}...")
        items = search_vinted(recherche["params"])
        
        nouveaux = 0
        deals = 0
        
        for item in items:
            item_id = str(item.get("id", ""))
            
            if item_id in seen_ids:
                continue
            
            seen_ids.add(item_id)
            nouveaux += 1
            
            # Analyser la plus-value
            affaire = analyser_article(item)
            
            if affaire:
                deals += 1
                total_deals += 1
                
                # Log console
                print(f"\n{Fore.GREEN}  🔥 DEAL TROUVÉ !")
                print(f"  {affaire['emoji_marque']} {affaire['marque'].upper()} — {affaire['titre'][:50]}")
                print(f"  💰 {affaire['prix']}€ | Marché: {affaire['prix_marche']}€ | +{affaire['marge']}%")
                print(f"  🔗 {affaire['url']}")
                
                # Alerte Telegram
                send_alert(affaire)
        
        total_new += nouveaux
        if nouveaux > 0:
            print(f"{Fore.WHITE}    ✓ {nouveaux} nouvelles annonces, {deals} deals")
        
        time.sleep(2)  # Pause entre les requêtes
    
    save_seen(seen_ids)
    
    if total_deals == 0:
        print(f"{Fore.YELLOW}  Aucun deal cette fois. {total_new} nouvelles annonces analysées.")
    else:
        print(f"\n{Fore.GREEN}✅ {total_deals} deal(s) envoyé(s) sur Telegram !")

# ═══════════════════════════════════════════════════════════════
#  🚀  LANCEMENT
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════╗
║       🤖  VINTED ARBITRAGE BOT  🤖               ║
║   Détecte les bonnes affaires automatiquement    ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.WHITE}Config:
  • Marges ciblées    : +{MIN_MARGE}% minimum
  • Marques suivies   : {len(MARQUES)}
  • Recherches actives: {len(RECHERCHES)}
  • Intervalle        : {CHECK_INTERVAL}s
  • Alertes           : Telegram
""")
    
    # Vérifier config Telegram
    if "TON_TOKEN" in TELEGRAM_TOKEN or "TON_CHAT" in TELEGRAM_CHAT_ID:
        print(f"{Fore.RED}⚠️  Configure TELEGRAM_TOKEN et TELEGRAM_CHAT_ID en haut du fichier !")
        print(f"{Fore.YELLOW}   1. Crée un bot via @BotFather sur Telegram")
        print(f"{Fore.YELLOW}   2. Récupère ton Chat ID via @userinfobot")
        print(f"{Fore.YELLOW}   3. Remplis les variables en haut du script\n")
        input("Appuie sur Entrée pour continuer quand même (sans Telegram)...")
    
    # Connexion Vinted
    print(f"{Fore.WHITE}🌐 Connexion à Vinted...")
    get_vinted_token()
    
    # Message de démarrage Telegram
    if "TON_TOKEN" not in TELEGRAM_TOKEN:
        asyncio.run(send_startup_message())
    
    # Première vérification immédiate
    check_vinted()
    
    # Planifier les vérifications suivantes
    schedule.every(CHECK_INTERVAL).seconds.do(check_vinted)
    
    print(f"\n{Fore.GREEN}✅ Bot lancé ! Vérification toutes les {CHECK_INTERVAL} secondes.")
    print(f"{Fore.WHITE}   Appuie sur Ctrl+C pour arrêter.\n")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
