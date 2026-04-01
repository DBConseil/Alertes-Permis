# PRD - Alertes Permis de Conduire

## Context

Les places d'examen au permis de conduire sont rares et les désistements sont captés en quelques secondes par d'autres candidats. Ce projet vise à créer un bot de surveillance automatisé qui détecte les créneaux libérés sur le portail RdvPermis de la Sécurité Routière et envoie une notification Telegram instantanée, permettant à l'utilisateur de réserver avant quiconque.

**URL cible** : `https://www.securite-routiere.gouv.fr/passer-son-permis-de-conduire/inscription-et-formation/reserver-en-ligne-sa-place-pour-le`

---

## Structure du Projet

```
Alertes-Permis/
├── main.py          # Point d'entrée, boucle principale de surveillance
├── config.py        # Configuration centralisée (constantes, sélecteurs CSS, paramètres)
├── .env             # Variables sensibles (credentials, token Telegram)
├── .env.example     # Template .env sans valeurs sensibles
├── requirements.txt # Dépendances Python
└── prd.md           # Ce document
```

---

## Fonctionnalités

### 1. Connexion Automatisée

| Élément | Détail |
|---|---|
| Méthode | Playwright (async) avec `playwright-stealth` |
| Identifiants | `EMAIL` et `PASSWORD` lus depuis `.env` via `python-dotenv` |
| Gestion session | Sauvegarde du `storage_state` (cookies/localStorage) dans un fichier JSON pour réutilisation entre les relances |
| Reconnexion | Si un sélecteur de page de login est détecté pendant le scraping, relancer automatiquement le flow de connexion |
| Timeouts | `wait_for_selector` avec timeout configurable (défaut : 15s) |

### 2. Navigation & Scraping

- Après connexion, naviguer vers la page de recherche de créneaux
- Paramètres de recherche : **ville** et/ou **département** configurables dans `.env` (`SEARCH_CITY`, `SEARCH_DEPARTMENT`)
- Lire la grille des créneaux via les sélecteurs CSS du DOM
- Parser chaque cellule de la grille pour extraire : date, heure, centre d'examen

### 3. Logique de Détection

- **Condition de déclenchement** : le contenu textuel de la grille diffère de `"Aucun créneau disponible"` (ou variantes)
- **Extraction** : date, heure, nom du centre
- **Déduplication** : stocker les créneaux déjà notifiés dans un `set()` en mémoire (clé = `f"{date}_{heure}_{centre}"`)
  - Un créneau déjà dans le set ne déclenche pas de nouvelle notification
  - Le set est vidé toutes les **6 heures** pour gérer les cas où un créneau réapparaît après annulation
  - Cela évite l'envoi de 50 alertes pour le même créneau

### 4. Notification Telegram

| Élément | Détail |
|---|---|
| Librairie | `python-telegram-bot` |
| Variables `.env` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| Contenu du message | Date, heure, centre, lien direct "Réserver" |
| Bouton inline | `InlineKeyboardButton("Reserver", url=<URL_RESERVATION>)` |
| Notification de démarrage | Message envoyé au lancement du bot pour confirmer qu'il tourne |

### 5. Anti-Bannissement

| Technique | Implémentation |
|---|---|
| Stealth | `playwright-stealth` appliqué au contexte du navigateur |
| Délais aléatoires | `asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))` entre chaque cycle (défaut : 45-90s) |
| Mouvements souris | Simulation de `mouse.move()` aléatoire avant chaque action clé |
| User-Agent rotation | Liste de 5+ User-Agents réalistes, rotation à chaque nouveau contexte navigateur |
| Proxy (prêt) | Variable `.env` `PROXY_URL` optionnelle (support HTTP/SOCKS5 via l'option `proxy` de Playwright) |
| Empreinte navigateur | `viewport` aléatoire dans une plage réaliste, `locale` et `timezone` configurés |

### 6. Robustesse (24h/24)

- **Boucle infinie** avec `try/except` global : toute exception est loggée et le cycle reprend
- **Reconnexion automatique** : si timeout ou erreur de navigation, fermer le contexte et en recréer un
- **Limite de tentatives** : après 5 erreurs consécutives, pause longue (5 min) avant de reprendre
- **Logging** : `logging` Python avec rotation des fichiers (`RotatingFileHandler`, 5 MB max, 3 backups)
- **Redémarrage navigateur** : toutes les 2h, fermer et relancer le navigateur pour éviter les fuites mémoire

---

## Configuration (.env)

```env
# Credentials RdvPermis
EMAIL=votre_email@example.com
PASSWORD=votre_mot_de_passe

# Recherche
SEARCH_CITY=Paris
SEARCH_DEPARTMENT=75

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=987654321

# Timings (secondes)
MIN_DELAY=45
MAX_DELAY=90
SELECTOR_TIMEOUT=15000

# Proxy (optionnel)
PROXY_URL=

# Logging
LOG_LEVEL=INFO
```

---

## Configuration (config.py)

Centralise :
- Chargement des variables `.env` via `dotenv`
- Constantes (sélecteurs CSS, URLs, liste User-Agents)
- Paramètres de timing et retry
- Configuration du logger

---

## Flux Principal (main.py)

```
1. Charger config
2. Lancer Playwright (headless)
3. Appliquer stealth + proxy + User-Agent aléatoire
4. Se connecter (ou restaurer session)
5. BOUCLE INFINIE :
   a. Naviguer vers la page de recherche
   b. Remplir ville/département
   c. Lire la grille des créneaux
   d. Si créneau trouvé ET non déjà notifié :
      -> Envoyer notification Telegram
      -> Ajouter au set de déduplication
   e. Simuler mouvement souris
   f. Attendre délai aléatoire
   g. Si erreur : tenter reconnexion
   h. Si 5 erreurs consécutives : pause longue
   i. Toutes les 2h : redémarrer le navigateur
```

---

## Optimisations Performance

- **Headless strict** : pas de rendu graphique inutile
- **Bloquer les ressources inutiles** : via `route.abort()` sur images, CSS, fonts, media pour accélérer le chargement
- **`wait_for_selector`** au lieu de `wait_for_load_state("networkidle")` : plus rapide, cible uniquement l'élément pertinent
- **Réutilisation de page** : ne pas recréer une page à chaque cycle, simplement `goto()` + refresh
- **Async natif** : `asyncio` pour ne pas bloquer pendant les `sleep`

---

## Dépendances (requirements.txt)

```
playwright>=1.40
playwright-stealth>=1.0
python-telegram-bot>=20.0
python-dotenv>=1.0
```

---

## Vérification / Test

1. Créer le `.env` avec de vraies credentials
2. `pip install -r requirements.txt && playwright install chromium`
3. Lancer `python main.py`
4. Vérifier dans les logs : connexion réussie, navigation OK, cycle de scraping actif
5. Vérifier sur Telegram : message de démarrage reçu
6. Simuler un créneau disponible (ou attendre un vrai désistement) et vérifier la notification avec bouton "Réserver"
7. Vérifier la déduplication : le même créneau ne doit pas générer 2 notifications consécutives
