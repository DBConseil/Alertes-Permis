"""
selector_finder.py
------------------
Script utilitaire à lancer UNE SEULE FOIS, en mode non-headless (navigateur visible).
Il ouvre le portail, se connecte, puis inspecte le DOM et affiche les sélecteurs
candidats pour chaque étape du flow.

Usage :
    python selector_finder.py

Résultat : un bloc JSON prêt à coller dans config.py > SELECTORS
"""

import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

EMAIL = os.getenv("EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")
TARGET_URL = (
    "https://www.securite-routiere.gouv.fr/passer-son-permis-de-conduire/"
    "inscription-et-formation/reserver-en-ligne-sa-place-pour-le"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def find_inputs(page) -> list[dict]:
    """Retourne tous les <input> et <button> visibles avec leurs attributs utiles."""
    return await page.evaluate("""() => {
        const els = [...document.querySelectorAll('input, button, select, textarea, a[href]')];
        return els
            .filter(el => {
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0;
            })
            .map(el => ({
                tag: el.tagName.toLowerCase(),
                type: el.type || null,
                id: el.id || null,
                name: el.name || null,
                placeholder: el.placeholder || null,
                className: el.className || null,
                text: (el.innerText || el.value || '').trim().slice(0, 80),
                href: el.href || null,
            }));
    }""")


async def find_containers(page) -> list[dict]:
    """Retourne les éléments susceptibles de contenir la grille de créneaux."""
    return await page.evaluate("""() => {
        const keywords = ['slot', 'creneau', 'créneau', 'result', 'calendar',
                          'table', 'grid', 'dispo', 'available', 'booking'];
        const els = [...document.querySelectorAll('*')];
        return els
            .filter(el => {
                const r = el.getBoundingClientRect();
                if (r.width < 100 || r.height < 50) return false;
                const cls = (el.className || '').toLowerCase();
                const id  = (el.id || '').toLowerCase();
                return keywords.some(k => cls.includes(k) || id.includes(k));
            })
            .slice(0, 20)
            .map(el => ({
                tag: el.tagName.toLowerCase(),
                id: el.id || null,
                className: el.className || null,
                childCount: el.children.length,
                text_preview: el.innerText.trim().slice(0, 120),
            }));
    }""")


async def find_no_slot_text(page) -> list[str]:
    """Cherche les variantes du message 'aucun créneau'."""
    return await page.evaluate("""() => {
        const keywords = ['aucun', 'disponible', 'no slot', 'complet', 'indisponible', 'aucune'];
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        const found = [];
        let node;
        while ((node = walker.nextNode())) {
            const t = node.textContent.trim();
            if (t.length > 5 && t.length < 200) {
                const lower = t.toLowerCase();
                if (keywords.some(k => lower.includes(k))) {
                    found.push(t);
                }
            }
        }
        return [...new Set(found)].slice(0, 10);
    }""")


# ---------------------------------------------------------------------------
# Flow principal
# ---------------------------------------------------------------------------

async def run():
    if not EMAIL or not PASSWORD:
        print("ERREUR : EMAIL et PASSWORD doivent être définis dans .env")
        sys.exit(1)

    async with async_playwright() as pw:
        # Mode visible pour pouvoir observer
        browser = await pw.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="fr-FR",
        )
        page = await context.new_page()

        print(f"\n[1] Navigation vers {TARGET_URL}")
        await page.goto(TARGET_URL, timeout=30000)
        await page.wait_for_load_state("networkidle")

        # Suivre les redirections éventuelles
        current_url = page.url
        print(f"    URL finale apres chargement : {current_url}")

        # Trouver les liens vers le portail de réservation
        links = await page.evaluate("""() => {
            return [...document.querySelectorAll('a[href]')]
                .map(a => ({ text: a.innerText.trim().slice(0, 80), href: a.href }))
                .filter(l => l.href && !l.href.startsWith('javascript'));
        }""")
        reservation_links = [
            l for l in links
            if any(k in l["href"].lower() or k in l["text"].lower()
                   for k in ["reserver", "rdv", "permis", "candidat", "inscription", "créneau"])
        ]
        if reservation_links:
            print("\n[2] Liens de réservation détectés :")
            for l in reservation_links:
                print(f"    [{l['text']}] → {l['href']}")
        else:
            print("\n[2] Aucun lien de réservation évident trouvé sur cette page.")

        print("\n[3] Champs visibles sur la page actuelle :")
        inputs = await find_inputs(page)
        for el in inputs:
            print(f"    {el}")

        # Si un lien de réservation a été trouvé, naviguer vers le premier
        if reservation_links:
            target = reservation_links[0]["href"]
            print(f"\n[4] Navigation vers le portail : {target}")
            await page.goto(target, timeout=30000)
            await page.wait_for_load_state("networkidle")
            print(f"    URL : {page.url}")

            print("\n[5] Champs sur la page de connexion/portail :")
            inputs2 = await find_inputs(page)
            for el in inputs2:
                print(f"    {el}")

        # Tentative de login
        print(f"\n[6] Tentative de connexion avec {EMAIL}")
        try:
            email_sel = await page.query_selector("input[type='email'], input[name='email'], #email")
            pass_sel  = await page.query_selector("input[type='password']")
            submit    = await page.query_selector("button[type='submit'], input[type='submit']")

            if email_sel and pass_sel and submit:
                await email_sel.fill(EMAIL)
                await asyncio.sleep(0.5)
                await pass_sel.fill(PASSWORD)
                await asyncio.sleep(0.5)
                await submit.click()
                await page.wait_for_load_state("networkidle")
                print(f"    URL apres login : {page.url}")
            else:
                print("    Formulaire de login non trouvé automatiquement.")
                print("    Connectez-vous manuellement dans le navigateur, puis appuyez sur Entrée.")
                input()
        except Exception as exc:
            print(f"    Erreur login : {exc}")
            print("    Connectez-vous manuellement, puis appuyez sur Entrée.")
            input()

        # Après connexion : inspecter la page de recherche
        print(f"\n[7] URL apres connexion : {page.url}")
        print("\n[8] Champs de recherche détectés :")
        inputs3 = await find_inputs(page)
        for el in inputs3:
            print(f"    {el}")

        print("\n[9] Conteneurs candidats pour la grille de créneaux :")
        containers = await find_containers(page)
        for c in containers:
            print(f"    {c}")

        print("\n[10] Textes 'aucun créneau' candidats :")
        no_slot = await find_no_slot_text(page)
        for t in no_slot:
            print(f"    \"{t}\"")

        # Résumé JSON à coller dans config.py
        print("\n" + "="*60)
        print("RÉSUMÉ — Mettez à jour SELECTORS dans config.py avec ces infos")
        print("="*60)
        summary = {
            "url_portail": page.url,
            "champs_detectes": inputs3[:15],
            "conteneurs_creneaux": containers[:5],
            "textes_aucun_creneau": no_slot,
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

        print("\nFermez le navigateur ou appuyez sur Entrée pour terminer.")
        input()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
