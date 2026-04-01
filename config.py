import logging
import os
import random
import sys
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------
EMAIL = os.getenv("EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")

# ---------------------------------------------------------------------------
# Recherche
# ---------------------------------------------------------------------------
SEARCH_CITY = os.getenv("SEARCH_CITY", "")
SEARCH_DEPARTMENT = os.getenv("SEARCH_DEPARTMENT", "")

# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ---------------------------------------------------------------------------
# Timings
# ---------------------------------------------------------------------------
MIN_DELAY = float(os.getenv("MIN_DELAY", "45"))
MAX_DELAY = float(os.getenv("MAX_DELAY", "90"))
SELECTOR_TIMEOUT = int(os.getenv("SELECTOR_TIMEOUT", "15000"))

# Pause longue après 5 erreurs consécutives (secondes)
LONG_PAUSE = int(os.getenv("LONG_PAUSE", "300"))

# Redémarrage navigateur toutes les X secondes (défaut : 2h)
BROWSER_RESTART_INTERVAL = int(os.getenv("BROWSER_RESTART_INTERVAL", "7200"))

# Vidage du set de déduplication toutes les X secondes (défaut : 6h)
DEDUP_RESET_INTERVAL = int(os.getenv("DEDUP_RESET_INTERVAL", "21600"))

# ---------------------------------------------------------------------------
# Proxy
# ---------------------------------------------------------------------------
PROXY_URL = os.getenv("PROXY_URL", "")  # ex: "http://user:pass@host:port"

# ---------------------------------------------------------------------------
# URLs
# ---------------------------------------------------------------------------
BASE_URL = "https://www.securite-routiere.gouv.fr"
SEARCH_URL = (
    "https://www.securite-routiere.gouv.fr/passer-son-permis-de-conduire/"
    "inscription-et-formation/reserver-en-ligne-sa-place-pour-le"
)
RESERVATION_URL = SEARCH_URL

# ---------------------------------------------------------------------------
# Sélecteurs CSS  (à affiner après inspection du DOM réel)
# ---------------------------------------------------------------------------
SELECTORS = {
    # Page de connexion
    "login_email": "input[type='email'], input[name='email'], #email",
    "login_password": "input[type='password'], input[name='password'], #password",
    "login_submit": "button[type='submit'], input[type='submit']",
    "login_indicator": "input[type='email']",  # présent = on est sur la page login

    # Recherche de créneaux
    "search_city": "input[placeholder*='ville'], input[name*='city'], input[id*='city']",
    "search_department": "input[placeholder*='département'], input[name*='department']",
    "search_submit": "button[type='submit']",

    # Grille des créneaux
    "slots_container": ".slots, .creneaux, [class*='slot'], [class*='creneau'], table",
    "no_slot_text": "Aucun créneau disponible",

    # Cellule individuelle d'un créneau
    "slot_date": "[class*='date'], td:nth-child(1)",
    "slot_time": "[class*='heure'], [class*='time'], td:nth-child(2)",
    "slot_center": "[class*='centre'], [class*='center'], td:nth-child(3)",
}

# ---------------------------------------------------------------------------
# User-Agents réalistes
# ---------------------------------------------------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
    "Gecko/20100101 Firefox/125.0",
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
    {"width": 1280, "height": 800},
    {"width": 1536, "height": 864},
]

# Fichier de sauvegarde de session Playwright
SESSION_FILE = "storage_state.json"

# Fichier de persistance de la déduplication
DEDUP_FILE = "notified_slots.json"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

_handler_file = RotatingFileHandler(
    "alertes_permis.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
_handler_console = logging.StreamHandler()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[_handler_file, _handler_console],
)

logger = logging.getLogger("alertes_permis")


# ---------------------------------------------------------------------------
# Validation au démarrage
# ---------------------------------------------------------------------------

def validate() -> None:
    """Vérifie que toutes les variables critiques sont définies. Quitte si non."""
    errors = []
    if not EMAIL:
        errors.append("EMAIL manquant dans .env")
    if not PASSWORD:
        errors.append("PASSWORD manquant dans .env")
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN manquant dans .env")
    if not TELEGRAM_CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID manquant dans .env")
    if not SEARCH_CITY and not SEARCH_DEPARTMENT:
        errors.append("SEARCH_CITY ou SEARCH_DEPARTMENT doit être défini dans .env")
    if MIN_DELAY >= MAX_DELAY:
        errors.append(f"MIN_DELAY ({MIN_DELAY}) doit être < MAX_DELAY ({MAX_DELAY})")

    if errors:
        for err in errors:
            logger.error("Configuration invalide : %s", err)
        sys.exit(1)


def random_user_agent() -> str:
    return random.choice(USER_AGENTS)


def random_viewport() -> dict:
    return random.choice(VIEWPORTS)
