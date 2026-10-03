# -*- coding: utf-8 -*-
"""Contenu du portfolio — transcription fidèle de _sources/brief/construction portfolio.docx

Hiérarchie du docx :
  gras (sz28)          → les 2 grandes sections        → SECTIONS
  gras rouge (#EE0000) → les rubriques de « Mes productions » → RUBRIQUES
  souligné             → une production individuelle   → "titre"
  texte courant        → son explication               → "texte"
  gris (#BFBFBF)       → les ressources visuelles liées → "ressources"

Pour modifier un texte du site, c'est ici — puis relancer :
    python3 scripts/build.py
"""

IDENTITE = {
    "nom": "Lila Narinx",
    "role": "Social media, content creation, digital strategy",
    "email": "lila.narinx@gmail.com",
    "tel": "+32 471 45 51 77",
    "tel_lien": "+32471455177",
    "linkedin": "",            # ← à compléter si Lila veut l'afficher
    "domaine": "lilanarinx.com",
}

PRESENTATION = {
    "titre": "Présentation générale",
    "texte": (
        "J’ai toujours été animée par la création "
        "que ce soit à travers le graphisme, la photographie, la vidéo, ou "
        "encore la rédaction. Aujourd’hui diplômée en Relations Publiques "
        "(IHECS) et Marketing (ICHEC), je me spécialise en social media et "
        "création de contenu. J’aime combiner réflexion stratégique, concepts "
        "créatifs et production de contenus pour construire des univers de "
        "marque cohérents et engageants."
    ),
    "portrait": "assets/img/portrait.webp",
}

# Repères affichés en petit sous le portrait — tirés du CV.
REPERES = [
    ("Master RP", "IHECS — E-RP & Data intelligence"),
    ("Master marketing", "ICHEC — gestion & marketing"),
    ("Freelance", "digital strategy & content creation"),
    ("Cofondatrice", "Caerus asbl"),
]

TITRE_PRODUCTIONS = "Mes productions"

CONFIDENTIEL = (
    "Cette campagne étant confidentielle, je me permets de vous demander de ne "
    "pas diffuser les productions médiatiques qui vous sont partagées. "
    "Cependant, n’hésitez pas à me contacter pour recevoir les dossiers de "
    "campagne, de réseaux sociaux et de communication interne en entier si cela "
    "vous intéresse."
)

TRIBE = (
    "Durant mon stage de 3 mois réalisé chez Tribe Agency, une agence de "
    "communication et relations publiques évoluant dans le secteur Food & "
    "Beverage et Horeca, "
)


def img(*nums):
    """Déclare des visuels par leur numéro de brief."""
    return [{"type": "image", "n": n} for n in nums]


def vid(*noms):
    """Déclare des vidéos par leur nom de fichier (sans extension).
    « nom:12 » démarre la lecture à 12 secondes (fragment média #t=12,
    standard HTML5 — pas de retouche du fichier)."""
    out = []
    for n in noms:
        nom, _, debut = n.partition(":")
        d = {"type": "video", "f": nom}
        if debut:
            d["debut"] = int(debut)
        out.append(d)
    return out


RUBRIQUES = [
    # ──────────────────────────────────────────────────────────────────
    {
        "id": "campagne-360",
        "titre": "Campagne 360°",
        "productions": [{
            "titre": "Campagne RP pour Takeaway.com",
            "texte": (
                "Dans le cadre de mon master en Relations Publiques à l’IHECS, "
                "j’ai eu une année pour réaliser, en équipe, une campagne de "
                "communication complète autour d’une problématique réelle "
                "donnée par la marque Takeaway.com. Un projet formateur mêlant "
                "stratégie, créativité et travail collectif, présenté devant un "
                "jury professionnel et récompensé par une grande distinction. "
                "En voici les points importants :"
            ),
            "note": CONFIDENTIEL,
            "ressources": "Contenus 1 à 8",
            "medias": img(1, 2, 3, 4, 5, 6, 7, 8),
            "cols": 4,
        }],
    },
    # ──────────────────────────────────────────────────────────────────
    {
        "id": "reseaux-sociaux",
        "titre": "Réseaux sociaux",
        "productions": [
            {
                "titre": "Stage chez Tribe Agency",
                "texte": (
                    TRIBE + "j’ai eu la chance de pouvoir gérer plusieurs "
                    "comptes clients sur Instagram (ceux des restaurants La "
                    "Stazione, FightClub et Vérigoud ainsi que le compte "
                    "professionnel de l’agence). Vous trouverez ci-joint "
                    "certains contenus (posts/stories) que j’ai réalisés ainsi "
                    "que des vues d’ensemble des feeds que j’ai mis en place."
                ),
                "ressources": "Contenus 9 à 20",
                "medias": img(9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20),
                "cols": 4,
            },
            {
                "titre": "Publications Instagram pour mon client « Voyage Brazil Selection »",
                "ressources": "Contenus 21 à 22",
                "medias": img(21, 22),
                "cols": 4,
            },
            {
                "titre": "Publications Instagram pour l’asbl CAERUS dont je suis cofondatrice",
                "ressources": "Contenu 23",
                "medias": img(23),
                "cols": 4,
            },
            {
                "titre": "Publications Linkedin et nouvelle bannière pour mon client Venthone Consulting",
                "ressources": "Contenus 24 à 31",
                "medias": img(24, 25, 26, 27, 28, 29, 30, 31),
                "cols": 4,
            },
            {
                "titre": "Projet fictif universitaire",
                "texte": (
                    "Voici le contenu que j’ai réalisé pour un événement fictif "
                    "dans le cadre de mon cours de communication événementielle "
                    "à l’IHECS."
                ),
                "ressources": "Contenu 32",
                "medias": img(32),
                "cols": 4,
            },
        ],
    },
    # ──────────────────────────────────────────────────────────────────
    {
        "id": "sites-web",
        "titre": "Sites web",
        "productions": [{
            "titre": "Sites web rebrandés et redesignés pour mes clients Miège et Veyras",
            "ressources": "Contenus 33 à 38",
            "liens": [
                ("Voir le site Miège", "https://www.miege.be"),
                ("Voir le site Veyras", "https://www.veyrasconsulting.com/"),
            ],
            "medias": img(33, 34, 35, 36, 37, 38),
            "cols": 2,
        }],
    },
    # ──────────────────────────────────────────────────────────────────
    {
        "id": "photo",
        "titre": "Photo",
        "productions": [
            {
                "titre": "Stage chez Tribe Agency",
                "texte": (
                    TRIBE + "j’ai eu la chance de pouvoir participer à de "
                    "nombreux shootings. Vous trouverez ci-joint certains "
                    "moodboards que j’ai réalisés ainsi que quelques photos "
                    "emblématiques de ces shootings."
                ),
                "ressources": "Contenus 39 à 45",
                "medias": img(39, 40, 41, 42, 43, 44, 45),
                "cols": 3,
            },
            {
                "titre": "Photos réalisées pour la marque de boisson non alcoolisée « Vendredi Apér0% »",
                "ressources": "Contenus 46 à 49",
                "medias": img(46, 47, 48, 49),
                "cols": 4,
            },
        ],
    },
    # ──────────────────────────────────────────────────────────────────
    {
        "id": "video",
        "titre": "Vidéo",
        "productions": [
            {
                "titre": "Stage chez Tribe Agency",
                "texte": (
                    TRIBE + "j’ai eu la chance d’être responsable des contenus "
                    "vidéos à destination des réseaux sociaux (que ça soit la "
                    "prise de vue ou le montage). J’ai filmé et monté plus de "
                    "50 réels à destination des comptes Instagram de nos "
                    "clients, en voici quelques-uns (vidéos montées sur CapCut "
                    "Pro)."
                ),
                "ressources": "6 reels : AKAI sushi, Le Corbier, Gazzosa, Ono, Delhaize Champagne",
                "medias": vid(
                    "reel-akai-sushi", "reel-cocktail-le-corbier",
                    "reel-cuisine-gazzosa", "reel-post-it-ono",
                    "reel-cuisine-ono", "reel-cocktail-framboise-delhaize",
                ),
                "cols": 3,
                "boucle": True,
            },
            {
                "titre": "Contenus vidéo tournés et montés pour la marque de boisson non alcoolisée « Vendredi Apér0% » à destination d’Instagram",
                "ressources": "Contenus « apéro final » et « poker final »",
                "medias": vid("apero-final", "poker-final"),
                "cols": 3,
                "boucle": True,
            },
            {
                "titre": "Contenu vidéo reportage sur l’artiste bruxellois « Spear », réalisé dans le cadre d’un cours de vidéo à l’IHECS",
                "ressources": "Contenu « projet final SPEAR »",
                "medias": vid("projet-spear:13"),
                "cols": 1,
            },
            {
                "titre": "Vidéos publicitaires tournées et montées dans le cadre d’un cours nommé « Audiovisual, Technology and Communication » suivi durant mon Erasmus",
                "ressources": "Contenus 75 à 76",
                "medias": vid("pub-erasmus-1", "pub-erasmus-2"),
                "cols": 2,
            },
        ],
    },
    # ──────────────────────────────────────────────────────────────────
    {
        "id": "redaction",
        "titre": "Rédaction",
        "productions": [
            {
                "titre": "Stage chez Tribe Agency",
                "texte": (
                    TRIBE + "j’ai eu la chance de pouvoir m’occuper de la "
                    "présence de plusieurs marques dans la presse notamment à "
                    "travers la rédaction de newsletter à destination d’une "
                    "database de journalistes spécifiques. En voici un exemple "
                    "réalisé pour présenter certains de nos clients "
                    "intéressants à aborder à l’occasion de la fête des mères."
                ),
                "ressources": "Contenus 50 à 51",
                "medias": img(50, 51),
                "cols": 2,
            },
            {
                "titre": "Rédaction d’articles de blog pour Venthone Consulting",
                "ressources": "Contenus 52 à 53",
                "medias": img(52, 53),
                "cols": 2,
            },
            {
                "titre": "Communiqués de presse rédigés dans le cadre de mes cours d’expression écrite suivis à l’IHECS",
                "ressources": "Contenus 54 à 55",
                "medias": img(54, 55),
                "cols": 2,
            },
        ],
    },
    # ──────────────────────────────────────────────────────────────────
    {
        "id": "graphisme",
        "titre": "Graphisme",
        "productions": [
            {
                "titre": "Réalisation d’affiches pour Takeaway.com",
                "texte": (
                    "Dans le cadre de mon master en Relations Publiques à "
                    "l’IHECS, j’ai eu une année pour réaliser, en équipe, une "
                    "campagne de communication complète autour d’une "
                    "problématique réelle donnée par la marque Takeaway.com. Un "
                    "projet formateur mêlant stratégie, créativité et travail "
                    "collectif, présenté devant un jury professionnel et "
                    "récompensé par une grande distinction. Voici les affiches "
                    "que j’ai réalisées pour cette campagne."
                ),
                "note": (
                    "Celle-ci étant confidentielle, je me permets de vous "
                    "demander de ne pas diffuser les productions médiatiques "
                    "qui vous sont partagées."
                ),
                "ressources": "Contenus 56 à 58",
                "medias": img(56, 57, 58),
                "cols": 3,
                # bloc secondaire rattaché à la même production (non souligné
                # dans le docx) :
                "suite": {
                    "texte": "Ainsi que les différents dossiers de campagne réalisés sur Indesign :",
                    "ressources": "Contenus 59 à 60",
                    "medias": img(59, 60),
                    "cols": 2,
                },
            },
            {
                "titre": "Pochette de CD réalisée dans le cadre de mon cours de graphisme suivi à l’IHECS",
                "ressources": "Contenu 61",
                "medias": img(61),
                "cols": 2,
            },
            {
                "titre": "Affiche réalisée dans le cadre d’un cours de graphisme suivi à l’IHECS",
                "ressources": "Contenu 62",
                "medias": img(62),
                "cols": 3,
            },
            {
                "titre": "Flyer et carte de visite réalisés dans le cadre d’un projet médiatique à l’IHECS",
                "ressources": "Contenus 63 à 66",
                "medias": img(65, 66, 63, 64),
                "cols": 2,
            },
            {
                "titre": "Logo et affiches réalisés pour un événement fictif dans le cadre d’un cours de communication événementielle à l’IHECS",
                "ressources": "Contenus 67 à 68",
                "medias": img(67, 68),
                "cols": 3,
            },
        ],
    },
    # ──────────────────────────────────────────────────────────────────
    {
        "id": "intelligence-artificielle",
        "titre": "Intelligence artificielle",
        "productions": [{
            "titre": "Projet scolaire",
            "texte": (
                "Dans le cadre de mon cours de Nouvelles Technologies "
                "Créatives, j’ai réalisé un projet expérimental combinant "
                "intelligence artificielle, storytelling et stratégie digitale. "
                "L’objectif était de donner vie sur les réseaux sociaux à une "
                "personnalité historique, en l’occurrence Cléopâtre, imaginée "
                "comme une influenceuse contemporaine. J’ai développé une "
                "stratégie digitale complète sur les réseaux sociaux autour de "
                "sa personnalité, ses routines quotidiennes et ses intérêts, en "
                "adaptant son image aux codes actuels."
            ),
            "texte2": (
                "Toutes les images, voix, musiques et vidéos du projet ont été "
                "entièrement créées à l’aide d’outils d’intelligence "
                "artificielle (Midjourney, Replicate, Picsi, Face Swapp, "
                "Rendernet, ElevenLabs, Suno, Runway et Heygen), à partir d’une "
                "sculpture antique. Le résultat est une incarnation réaliste et "
                "dynamique d’une Cléopâtre moderne active sur les réseaux "
                "sociaux."
            ),
            "ressources": "Contenus 69 à 74",
            "medias": img(69, 70, 71, 72, 73, 74),
            "cols": 3,
            # série homogène : grille régulière plutôt que collage éditorial
            "grille": True,
        }],
    },
]
