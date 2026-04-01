"""
Alertes Permis de Conduire
Bot de surveillance 24/7 des créneaux disponibles sur RdvPermis.
"""

import asyncio
import os
import random
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
# ---------------------------------------------------------------------------

BLOCKED_TYPES = {"image", "media", "font", "stylesheet"}


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

    # Réutiliser la session si disponible
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

        # Vérifier si une page de login est présente
        login_el = await page.query_selector(config.SELECTORS["login_indicator"])
        if not login_el:
            logger.info("Session déjà active, pas besoin de se reconnecter.")
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

        # Sauvegarder la session
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
    try:
        await page.goto(config.SEARCH_URL, timeout=config.SELECTOR_TIMEOUT)
        await _mouse_wiggle(page)

        # Remplir ville / département si des sélecteurs correspondent
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

        # Soumettre la recherche
        submit_el = await page.query_selector(config.SELECTORS["search_submit"])
        if submit_el:
            await _mouse_wiggle(page)
            await submit_el.click()

        # Attendre le conteneur de résultats
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

        # Parser les créneaux disponibles
        slots: list[dict] = []
        rows = await container.query_selector_all("tr, [class*='slot'], [class*='creneau']")

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

    except PlaywrightTimeout:
        logger.warning("Timeout lors du scraping.")
        raise
    except Exception as exc:
        logger.error("Erreur scraping : %s", exc)
        raise


# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------

async def run() -> None:
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

    await send_telegram(
        bot,
        "Bot Alertes Permis demarre.\n"
        f"Surveillance de : <b>{config.SEARCH_CITY or config.SEARCH_DEPARTMENT}</b>",
    )

    notified: set[str] = set()
    consecutive_errors = 0
    last_browser_restart = time.monotonic()
    last_dedup_reset = time.monotonic()

    async with async_playwright() as pw:
        browser, context = await create_context(pw)
        page = await context.new_page()

        if STEALTH_AVAILABLE:
            await stealth_async(page)

        connected = await login(page)
        if not connected:
            logger.error("Impossible de se connecter. Arret.")
            await browser.close()
            return

        while True:
            now = time.monotonic()

            # Vidage périodique de la déduplication (6h)
            if now - last_dedup_reset > config.DEDUP_RESET_INTERVAL:
                notified.clear()
                last_dedup_reset = now
                logger.info("Set de deduplication reinitialise.")

            # Redémarrage périodique du navigateur (2h)
            if now - last_browser_restart > config.BROWSER_RESTART_INTERVAL:
                logger.info("Redemarrage du navigateur (maintenance 2h).")
                await browser.close()
                browser, context = await create_context(pw)
                page = await context.new_page()
                if STEALTH_AVAILABLE:
                    await stealth_async(page)
                await login(page)
                last_browser_restart = time.monotonic()

            try:
                slots = await scrape_slots(page)
                consecutive_errors = 0

                for slot in slots:
                    key = f"{slot['date']}_{slot['heure']}_{slot['centre']}"
                    if key in notified:
                        continue

                    notified.add(key)
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

                # Recréer le contexte en cas d'erreur grave
                try:
                    await context.close()
                except Exception:
                    pass
                try:
                    _, context = await create_context(pw)
                    page = await context.new_page()
                    if STEALTH_AVAILABLE:
                        await stealth_async(page)
                    await login(page)
                    last_browser_restart = time.monotonic()
                except Exception as reinit_exc:
                    logger.error("Echec reinitialisation : %s", reinit_exc)

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


if __name__ == "__main__":
    asyncio.run(run())
