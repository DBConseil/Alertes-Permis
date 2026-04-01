# PROMPT ARTEFACT — Creation de Videos Promotionnelles
# Service : Alertes Permis de Conduire
# =====================================================

# -------------------------------------------------------
# VARIABLES A REMPLIR AVANT UTILISATION
# -------------------------------------------------------
NOM_SERVICE = "[NOM DU SERVICE]"          # Ex: PermisFlash, AlertePermis
PRIX = "[PRIX]"                            # Ex: "9.99/mois", "Gratuit", "19.99 one-shot"
VILLE = "[VILLE]"                          # Ex: Paris, Lyon, Marseille
LIEN_INSCRIPTION = "[LIEN]"               # Ex: URL du formulaire ou du bot Telegram
TIKTOK_HANDLE = "[@ TIKTOK]"              # Ex: @alertepermis


# =======================================================
# SECTION 1 — SCRIPTS REELS (10 scripts prets a l'emploi)
# =======================================================

SCRIPTS = [

# -------------------------------------------------------
# SCRIPT 1 — Le Hook Choc (Format: Screen Recording)
# Duree: 15-20s | Style: Notif Telegram a l'ecran
# -------------------------------------------------------
"""
[VISUEL] Screen recording telephone, ecran d'accueil

[HOOK - 3s]
(Notif Telegram apparait)
VOIX OFF: "Ca, c'est le son que t'entends quand une place de permis se libere..."

[CORPS - 8s]
(On voit le message: CRENEAU DISPONIBLE - Date - Centre)
VOIX OFF: "Pendant que les autres refreshent la page depuis 3 mois,
mon bot detecte les desistements en temps reel et m'envoie une alerte
en moins de 30 secondes."

[CTA - 4s]
VOIX OFF: "Lien en bio. Prochaine place, c'est la tienne."
(Texte a l'ecran: {NOM_SERVICE} - Lien en bio)
""",

# -------------------------------------------------------
# SCRIPT 2 — Le Storytelling (Format: Face cam ou voix off)
# Duree: 30s | Style: Temoignage perso
# -------------------------------------------------------
"""
[HOOK - 3s]
"J'ai eu ma place de permis en 2h. Voila comment."

[CORPS - 20s]
"Y'a 2 semaines j'avais ZERO place disponible a {VILLE}.
Delai officiel: 3 a 4 mois. J'ai active {NOM_SERVICE}.
C'est un bot qui surveille le site de la Securite Routiere 24h/24.
Des qu'un desistement tombe, notif instantanee sur mon telephone.
2 heures apres l'activation: BOUM, creneau detecte, j'ai reserve."

[CTA - 5s]
"Si t'en as marre d'attendre, le lien est en bio."
""",

# -------------------------------------------------------
# SCRIPT 3 — Le Comparatif (Format: Split screen / Texte)
# Duree: 15s | Style: Texte anime
# -------------------------------------------------------
"""
[ECRAN SPLIT]

GAUCHE:                          DROITE:
"Les autres"                     "Toi avec {NOM_SERVICE}"
- Refresh F5 toute la journee    - Tu recois une notif
- 3 mois d'attente               - Place en 24-48h
- Rate les desistements          - Alerte en 30 secondes
- Stress                         - Tranquille

[CTA]
"Lien en bio — {PRIX}"
""",

# -------------------------------------------------------
# SCRIPT 4 — Le Chiffre Choc (Format: Voix off + texte)
# Duree: 12s | Style: Minimaliste
# -------------------------------------------------------
"""
[HOOK - 3s]
(Texte gros: "97%")
VOIX OFF: "97% des desistements sont repris en moins de 2 minutes."

[CORPS - 5s]
(Texte: "Sauf si t'as un bot qui te previent AVANT tout le monde")
VOIX OFF: "Sauf si t'as un bot qui te previent avant tout le monde."

[CTA - 4s]
"{NOM_SERVICE} — Lien en bio"
""",

# -------------------------------------------------------
# SCRIPT 5 — Le POV (Format: Texte + musique trending)
# Duree: 10s | Style: POV TikTok
# -------------------------------------------------------
"""
(Musique trending)

[Texte ecran, gros caracteres, rythme avec la musique]

"POV: t'attends ta place de permis depuis 4 mois"

"Tu actives {NOM_SERVICE}"

(Notif Telegram: CRENEAU DISPONIBLE)

"2h plus tard:"

(Screen de la reservation confirmee)

"Lien en bio."
""",

# -------------------------------------------------------
# SCRIPT 6 — La Preuve Sociale (Format: Compilation screenshots)
# Duree: 20s | Style: Temoignages
# -------------------------------------------------------
"""
[HOOK - 3s]
"Ils ont tous eu leur place en moins de 48h."

[CORPS - 12s]
(Defilement de screenshots de messages/temoignages)
"Merci j'ai eu ma place en 3h"
"Ca fait 4 mois que j'attendais, resolu en une nuit"
"Le bot m'a envoye une alerte a 6h du mat, j'ai reserve direct"

[CTA - 5s]
"Rejoins-les. {NOM_SERVICE}, lien en bio."
""",

# -------------------------------------------------------
# SCRIPT 7 — Le Tuto Rapide (Format: Screen recording)
# Duree: 25s | Style: How-to
# -------------------------------------------------------
"""
[HOOK - 3s]
"Comment avoir une place de permis cette semaine:"

[CORPS - 17s]
(Screen recording etape par etape)
"Etape 1: Tu t'inscris sur {NOM_SERVICE}"
"Etape 2: Tu choisis ta ville — {VILLE}"
"Etape 3: Tu recois une notif des qu'une place se libere"
"Etape 4: Tu cliques sur Reserver"
"C'est tout."

[CTA - 5s]
"Lien en bio. {PRIX}."
""",

# -------------------------------------------------------
# SCRIPT 8 — Le Meme/Humour (Format: Meme + voix off)
# Duree: 10s | Style: Relatable
# -------------------------------------------------------
"""
(Meme template: "Mon plan vs la realite")

[ECRAN 1 - 5s]
"Mon plan: Passer le permis cet ete"
"La Securite Routiere: Prochain creneau disponible en Decembre"

[ECRAN 2 - 5s]
"Moi avec {NOM_SERVICE}:"
(Notif: CRENEAU DISPONIBLE - dans 3 jours)
"Lien en bio"
""",

# -------------------------------------------------------
# SCRIPT 9 — L'Urgence (Format: Texte rapide)
# Duree: 8s | Style: Urgence/FOMO
# -------------------------------------------------------
"""
(Texte rapide, fond rouge/noir)

"PLACES LIMITEES A {VILLE}"
"Les desistements tombent entre 6h et 8h du matin"
"T'es pas devant ton ecran a 6h"
"Ton bot, si."
"{NOM_SERVICE} — Lien en bio"
""",

# -------------------------------------------------------
# SCRIPT 10 — Le Q&A (Format: Face cam / voix off)
# Duree: 30s | Style: FAQ
# -------------------------------------------------------
"""
[HOOK - 3s]
"Question qu'on me pose tout le temps:"

[Q1 - 8s]
"C'est legal?"
"Oui. Le bot consulte le site public exactement comme toi avec ton navigateur.
Il le fait juste plus vite."

[Q2 - 8s]
"Ca marche vraiment?"
"Le bot tourne 24h/24. Des qu'un desistement tombe, t'es notifie
en moins de 30 secondes."

[Q3 - 6s]
"C'est combien?"
"{PRIX}. Si t'as pas de place en 7 jours, rembourse."

[CTA - 5s]
"Lien en bio."
""",
]


# =======================================================
# SECTION 2 — CAPTIONS & HASHTAGS
# =======================================================

CAPTIONS = [
    "3 mois d'attente? Non merci. Lien en bio.",
    "Le bot qui trouve ta place de permis pendant que tu dors.",
    "J'ai eu ma place en 2h au lieu de 3 mois. Comment? Lien en bio.",
    "Arretez de refresh F5, y'a mieux.",
    "Alerte en 30 secondes. Reservation en 2 minutes. Lien en bio.",
]

HASHTAGS = (
    "#permisdeconduire #permis #conduire #autoecole "
    "#codelaroute #permisb #conduite #examen "
    "#astuce #bonplan #hack #2026 "
    f"#{VILLE.lower().replace(' ', '')} "
    "#jeuneconucteur #apprenticonducteur"
)


# =======================================================
# SECTION 3 — PLANNING DE PUBLICATION
# =======================================================

PLANNING = """
SEMAINE TYPE (5 posts/semaine):

Lundi    → Script 1 ou 4 (Hook court, <15s) — TikTok + Reels
Mardi    → Poster dans 3 groupes Facebook (template message)
Mercredi → Script 2 ou 10 (Format long, storytelling) — TikTok + Reels
Jeudi    → Story: screenshot d'une vraie alerte Telegram
Vendredi → Script 5 ou 8 (Meme/POV, viral) — TikTok + Reels
Weekend  → Reposter le meilleur de la semaine + repondre aux commentaires

REGLES:
- Poster entre 7h-9h ou 18h-21h (pic d'audience 18-25 ans)
- Toujours repondre aux commentaires dans la 1ere heure
- Recycler les Reels qui marchent en changeant la musique
- Un Reel qui fait +10k vues → en faire une variation
"""


# =======================================================
# SECTION 4 — TEMPLATES MESSAGES GROUPES FACEBOOK
# =======================================================

FACEBOOK_TEMPLATES = [
"""
Salut le groupe,

Petit tips pour ceux qui galèrent à trouver une place de permis à {VILLE}:
j'ai utilisé un service qui surveille le site de la Sécurité Routière 24h/24
et qui envoie une notif Telegram dès qu'un désistement tombe.

J'ai eu ma place en moins de 48h alors que le délai affiché c'était 3 mois.

Si ça intéresse quelqu'un je peux envoyer le lien en MP.
(je préfère MP pour pas faire de pub sauvage)
""",

"""
Question: y'a que moi qui galère à trouver un créneau sur RdvPermis?

J'ai trouvé une astuce: un bot qui détecte les désistements en temps réel.
En gros tu reçois une alerte sur ton tel dès qu'une place se libère,
et t'as juste à cliquer pour réserver.

MP si vous voulez le lien.
""",

"""
Pour ceux qui attendent une place depuis des mois:
j'ai testé {NOM_SERVICE}, c'est un bot qui scanne les créneaux
disponibles et t'envoie une notification instantanée.

Résultat: place obtenue en 24h.

Hésitez pas en MP pour le lien.
""",
]


# =======================================================
# SECTION 5 — EMAIL PROSPECTION AUTO-ECOLES
# =======================================================

EMAIL_AUTOECOLE = """
Objet: Partenariat — Aidez vos élèves à trouver une place d'examen plus vite

Bonjour [NOM AUTO-ECOLE],

Je suis le créateur de {NOM_SERVICE}, un service d'alerte en temps réel
qui détecte les créneaux de permis disponibles sur RdvPermis.

Le problème que résolvent nos alertes: vos élèves attendent 3-4 mois
pour une place d'examen, ce qui génère de la frustration et bloque
leur parcours chez vous.

Ma proposition:
- Vous recommandez {NOM_SERVICE} à vos élèves
- Ils obtiennent une place en 24-72h au lieu de 3 mois
- Vous touchez [X%/X euros] par inscription

C'est gagnant-gagnant: vos élèves passent le permis plus vite,
votre taux de réussite perçu augmente, et vous avez une source
de revenus complémentaire.

Seriez-vous disponible pour un appel de 10 minutes cette semaine?

Cordialement,
[VOTRE NOM]
{NOM_SERVICE}
"""


# =======================================================
# SECTION 6 — PROMPT GENERATION VOIX OFF (ELEVENLABS / TTS)
# =======================================================

PROMPT_TTS = """
INSTRUCTIONS POUR LA VOIX OFF:

- Voix: Homme/Femme, 20-25 ans, français, ton decontracte
- Rythme: Rapide mais articule, style "pote qui te file un bon plan"
- Pas de ton commercial ou robotique
- Pauses de 0.5s apres chaque hook
- Accentuer les mots en MAJUSCULES dans le script
- Duree max: celle indiquee dans le script

PARAMETRES ELEVENLABS RECOMMANDES:
- Stability: 0.35 (plus expressif)
- Clarity: 0.75
- Style exaggeration: 0.4
"""


# =======================================================
# SECTION 7 — PROMPT CANVA (TEMPLATES VIDEO)
# =======================================================

PROMPT_CANVA = """
BRIEF POUR TEMPLATES VIDEO CANVA:

FORMAT: 1080x1920 (vertical, 9:16)
DUREE: 10-30 secondes selon le script

STYLE VISUEL:
- Fond: Noir ou bleu fonce (#0a0a23)
- Texte principal: Blanc, gras, grande taille (60-80pt)
- Accent: Vert neon (#00ff88) pour les mots cles
- Typo: Montserrat Bold ou Inter Black
- Animations: Texte qui apparait mot par mot (style CapCut)

ELEMENTS RECURRENTS:
- Logo/nom du service en bas a droite
- "Lien en bio" en derniere slide
- Icone Telegram quand on montre la notification
- Emoji de sirene pour les hooks d'urgence

TEMPLATES A CREER:
1. Template "Hook + CTA" (2 slides, 10s)
2. Template "Comparatif Split" (1 slide, 15s)
3. Template "Tuto 4 etapes" (5 slides, 25s)
4. Template "Temoignage" (3 slides, 20s)
5. Template "POV" (4 slides, 10s)
"""
