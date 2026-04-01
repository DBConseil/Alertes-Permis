"""
Alertes Permis de Conduire
Bot de surveillance 24/7 des créneaux disponibles sur RdvPermis.
"""

import asyncio
import json
import os
import random
import signal
import time

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeout,
    async_playwright,
)
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

try:
    from playwright_stealth import stealth_async
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False

import config
from config import logger

# ---------------------------------------------------------------------------
# Déduplication persistante
# ---------------------------------------------------------------------------

def load_notified() -> set[str]:
    """Charge les créneaux déjà notifiés depuis le fichier de persistance."""
    if not os.path.exists(config.DEDUP_FILE):
        return set()
    try:
        with open(config.DEDUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("slots", []))
    except Exception as exc:
        logger.warning("Impossible de lire %s : %s", config.DEDUP_FILE, exc)
        return set()


def save_notified(notified: set[str]) -> None:
    """Sauvegarde le set de déduplication sur disque."""
    try:
        with open(config.DEDUP_FILE, "w", encoding="utf-8") as f:
            json.dump({"slots": list(notified)}, f)
    except Exception as exc:
        logger.warning("Impossible de sauvegarder %s : %s", config.DEDUP_FILE, exc)


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

async def send_telegram(bot: Bot, text: str, url: str | None = None) -> None:
    """Envoie un message Telegram avec bouton optionnel."""
    reply_markup = None
    if url:
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Reserver", url=url)]]
        )
    try:
        await bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=text,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
    except Exception as exc:
        logger.error("Erreur Telegram : %s", exc)


# ---------------------------------------------------------------------------
# Ressources bloquées (optimisation vitesse)
# Stylesheet retiré : peut casser le rendu des SPA et les sélecteurs dynamiques
# ---------------------------------------------------------------------------

BLOCKED_TYPES = {"image", "media", "font"}


async def block_resources(route, request):
    if request.resource_type in BLOCKED_TYPES:
        await route.abort()
    else:
        await route.continue_()


# ---------------------------------------------------------------------------
# Création du contexte navigateur
# ---------------------------------------------------------------------------

async def create_context(playwright: Playwright) -> tuple[Browser, BrowserContext]:
    ua = config.random_user_agent()
    vp = config.random_viewport()

    launch_opts: dict = {"headless": True}
    context_opts: dict = {
        "user_agent": ua,
        "viewport": vp,
        "locale": "fr-FR",
        "timezone_id": "Europe/Paris",
    }

    if config.PROXY_URL:
        launch_opts["proxy"] = {"server": config.PROXY_URL}

    browser = await playwright.chromium.launch(**launch_opts)

    if os.path.exists(config.SESSION_FILE):
        context_opts["storage_state"] = config.SESSION_FILE

    context = await browser.new_context(**context_opts)
    await context.route("**/*", block_resources)

    return browser, context


# ---------------------------------------------------------------------------
# Connexion
# ---------------------------------------------------------------------------

async def login(page: Page) -> bool:
    """Tente de se connecter. Retourne True si succès."""
    logger.info("Connexion en cours...")
    try:
        await page.goto(config.SEARCH_URL, timeout=config.SELECTOR_TIMEOUT)
        await _mouse_wiggle(page)

        login_el = await page.query_selector(config.SELECTORS["login_indicator"])
        if not login_el:
            logger.info("Session deja active.")
            return True

        await page.fill(config.SELECTORS["login_email"], config.EMAIL)
        await asyncio.sleep(random.uniform(0.3, 0.8))
        await page.fill(config.SELECTORS["login_password"], config.PASSWORD)
        await asyncio.sleep(random.uniform(0.3, 0.8))
        await _mouse_wiggle(page)
        await page.click(config.SELECTORS["login_submit"])

        await page.wait_for_selector(
            config.SELECTORS["slots_container"],
            timeout=config.SELECTOR_TIMEOUT,
        )

        await page.context.storage_state(path=config.SESSION_FILE)
        logger.info("Connexion reussie. Session sauvegardee.")
        return True

    except PlaywrightTimeout:
        logger.warning("Timeout lors de la connexion.")
        return False
    except Exception as exc:
        logger.error("Erreur connexion : %s", exc)
        return False


# ---------------------------------------------------------------------------
# Simulation mouvement souris
# ---------------------------------------------------------------------------

async def _mouse_wiggle(page: Page) -> None:
    vp = page.viewport_size or {"width": 1280, "height": 800}
    x = random.randint(100, vp["width"] - 100)
    y = random.randint(100, vp["height"] - 100)
    await page.mouse.move(x, y)
    await asyncio.sleep(random.uniform(0.1, 0.3))


# ---------------------------------------------------------------------------
# Scraping d'un cycle
# ---------------------------------------------------------------------------

async def scrape_slots(page: Page) -> list[dict]:
    """
    Navigue vers la page de recherche, remplit les filtres,
    lit la grille et retourne la liste des créneaux trouvés.
    Chaque créneau est un dict {date, heure, centre}.
    """
    await page.goto(config.SEARCH_URL, timeout=config.SELECTOR_TIMEOUT)
    await _mouse_wiggle(page)

    if config.SEARCH_CITY:
        city_el = await page.query_selector(config.SELECTORS["search_city"])
        if city_el:
            await city_el.fill(config.SEARCH_CITY)
            await asyncio.sleep(random.uniform(0.2, 0.5))

    if config.SEARCH_DEPARTMENT:
        dept_el = await page.query_selector(config.SELECTORS["search_department"])
        if dept_el:
            await dept_el.fill(config.SEARCH_DEPARTMENT)
            await asyncio.sleep(random.uniform(0.2, 0.5))

    submit_el = await page.query_selector(config.SELECTORS["search_submit"])
    if submit_el:
        await _mouse_wiggle(page)
        await submit_el.click()

    container = await page.wait_for_selector(
        config.SELECTORS["slots_container"],
        timeout=config.SELECTOR_TIMEOUT,
    )
    if not container:
        return []

    container_text = await container.inner_text()

    if config.SELECTORS["no_slot_text"].lower() in container_text.lower():
        logger.debug("Aucun creneau disponible.")
        return []

    slots: list[dict] = []
    rows = await container.query_selector_all(
        "tr, [class*='slot'], [class*='creneau']"
    )

    for row in rows:
        text = (await row.inner_text()).strip()
        if not text or config.SELECTORS["no_slot_text"].lower() in text.lower():
            continue

        date_el = await row.query_selector(config.SELECTORS["slot_date"])
        time_el = await row.query_selector(config.SELECTORS["slot_time"])
        center_el = await row.query_selector(config.SELECTORS["slot_center"])

        date = (await date_el.inner_text()).strip() if date_el else "?"
        heure = (await time_el.inner_text()).strip() if time_el else "?"
        centre = (await center_el.inner_text()).strip() if center_el else text[:60]

        if date and heure and centre:
            slots.append({"date": date, "heure": heure, "centre": centre})

    return slots


# ---------------------------------------------------------------------------
# Réinitialisation du navigateur
# ---------------------------------------------------------------------------

async def restart_browser(
    pw: Playwright,
    browser: Browser,
) -> tuple[Browser, BrowserContext, Page, bool]:
    """Ferme le navigateur existant et en crée un nouveau. Retourne (browser, context, page, connected)."""
    try:
        await browser.close()
    except Exception:
        pass

    new_browser, new_context = await create_context(pw)
    new_page = await new_context.new_page()

    if STEALTH_AVAILABLE:
        await stealth_async(new_page)

    connected = await login(new_page)
    return new_browser, new_context, new_page, connected


# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------

async def run() -> None:
    config.validate()

    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

    # Vérification de la connexion Telegram au démarrage
    try:
        await bot.get_me()
    except Exception as exc:
        logger.error("Impossible de joindre Telegram : %s", exc)
        raise SystemExit(1) from exc

    notified: set[str] = load_notified()
    consecutive_errors = 0
    last_browser_restart = time.monotonic()
    last_dedup_reset = time.monotonic()
    shutdown = False

    def _handle_signal(sig, frame):
        nonlocal shutdown
        logger.info("Signal %s recu, arret en cours...", sig)
        shutdown = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    await send_telegram(
        bot,
        "Bot Alertes Permis demarre.\n"
        f"Surveillance de : <b>{config.SEARCH_CITY or config.SEARCH_DEPARTMENT}</b>",
    )

    async with async_playwright() as pw:
        browser, context = await create_context(pw)
        page = await context.new_page()

        if STEALTH_AVAILABLE:
            await stealth_async(page)

        connected = await login(page)
        if not connected:
            logger.error("Impossible de se connecter. Arret.")
            await send_telegram(bot, "Echec de connexion au demarrage. Bot arrete.")
            await browser.close()
            return

        try:
            while not shutdown:
                now = time.monotonic()

                # Vidage périodique de la déduplication (défaut 6h)
                if now - last_dedup_reset > config.DEDUP_RESET_INTERVAL:
                    notified.clear()
                    save_notified(notified)
                    last_dedup_reset = now
                    logger.info("Set de deduplication reinitialise.")

                # Redémarrage périodique du navigateur (défaut 2h)
                if now - last_browser_restart > config.BROWSER_RESTART_INTERVAL:
                    logger.info("Redemarrage du navigateur (maintenance).")
                    browser, context, page, connected = await restart_browser(pw, browser)
                    last_browser_restart = time.monotonic()
                    if not connected:
                        logger.warning("Reconnexion echouee apres restart navigateur.")

                try:
                    slots = await scrape_slots(page)
                    consecutive_errors = 0

                    for slot in slots:
                        key = f"{slot['date']}_{slot['heure']}_{slot['centre']}"
                        if key in notified:
                            continue

                        notified.add(key)
                        save_notified(notified)

                        msg = (
                            "CRENEAU DISPONIBLE !\n\n"
                            f"Date : <b>{slot['date']}</b>\n"
                            f"Heure : <b>{slot['heure']}</b>\n"
                            f"Centre : <b>{slot['centre']}</b>"
                        )
                        logger.info("Creneau trouve : %s", key)
                        await send_telegram(bot, msg, url=config.RESERVATION_URL)

                except PlaywrightTimeout:
                    consecutive_errors += 1
                    logger.warning("Timeout (#%d).", consecutive_errors)

                    # Vérifier si session expirée → reconnexion
                    try:
                        login_el = await page.query_selector(
                            config.SELECTORS["login_indicator"]
                        )
                        if login_el:
                            logger.info("Session expiree, reconnexion...")
                            await login(page)
                    except Exception:
                        pass

                except Exception as exc:
                    consecutive_errors += 1
                    logger.error("Erreur inattendue (#%d) : %s", consecutive_errors, exc)

                    # Recréer le contexte navigateur complet
                    browser, context, page, connected = await restart_browser(pw, browser)
                    last_browser_restart = time.monotonic()
                    if connected:
                        consecutive_errors = 0  # recovery réussi
                    else:
                        logger.warning("Reconnexion echouee apres erreur.")

                if shutdown:
                    break

                # Pause longue si trop d'erreurs consécutives
                if consecutive_errors >= 5:
                    logger.warning(
                        "%d erreurs consecutives. Pause de %ds.",
                        consecutive_errors,
                        config.LONG_PAUSE,
                    )
                    await send_telegram(
                        bot,
                        f"Attention : {consecutive_errors} erreurs consecutives. "
                        f"Pause de {config.LONG_PAUSE // 60} min.",
                    )
                    await asyncio.sleep(config.LONG_PAUSE)
                    consecutive_errors = 0
                else:
                    delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
                    logger.debug("Prochain cycle dans %.0fs.", delay)
                    await asyncio.sleep(delay)

        finally:
            logger.info("Arret du bot.")
            save_notified(notified)
            try:
                await browser.close()
            except Exception:
                pass
            await send_telegram(bot, "Bot Alertes Permis arrete.")


if __name__ == "__main__":
    asyncio.run(run())
