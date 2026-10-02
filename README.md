# Portfolio — Lila Narinx

Site portfolio de Lila Narinx (social media & création de contenu), hébergé
gratuitement sur Cloudflare Pages, vidéos servies direct depuis Cloudflare R2.

Live : https://lilanarinx.com

## Stack

- **Site** : HTML/CSS/JS vanilla, zéro dépendance, **généré** par `scripts/build.py`
- **Hébergement site** : Cloudflare Pages (gratuit)
- **Hébergement vidéo** : Cloudflare R2 (`videos.lilanarinx.com`) — bascule
  automatique local → R2 dans `assets/js/site.js`
- **Domaine** : Cloudflare (déjà sur le compte)

## Comment modifier le site

| Je veux… | Je touche à… | Puis |
|---|---|---|
| changer un texte | `scripts/content.py` (transcrit le docx) | `python3 scripts/build.py` |
| changer le style | `assets/css/site.css` | rien, c'est direct |
| changer un comportement | `assets/js/site.js` | rien |
| ajouter / remplacer un visuel | `media/photos/<rubrique>/<n>.png` | `python3 scripts/optimize-images.py && python3 scripts/build.py` |
| ajouter une vidéo | `media/videos/…` + une ligne dans `scripts/optimize-videos.sh` et `scripts/posters.sh` | lancer les deux scripts, uploader le `.mp4` sur R2, build |
| changer la couverture d'une page | `COUVERTURES` dans `scripts/build.py` | build |

Ne jamais éditer les `.html` à la main : ils sont écrasés à chaque build.

Tester en local : `python3 -m http.server 4321` puis http://localhost:4321

## Design

Règle : **fond vert, textes blancs ou jaunes**. Le jaune `#feea94` vient du CV.
Pages : `index.html` (accueil : hero photo, présentation, index des 8
rubriques, contact) + une page par rubrique (couverture + titre qui chevauche
la photo, puis chaque production = texte collant à gauche / collage d'images
à droite, vidéos en lecture auto muette).

## ⚠️ Confidentialité

La campagne **Takeaway.com** est sous confidentialité (cf. brief) : les
productions ne doivent pas être diffusées publiquement. Ce repo est public —
`.gitignore` exclut donc le brief, le CV et les visuels sources restés à la
racine. Avant d'ajouter un visuel Takeaway dans `assets/`, vérifier qu'il est
diffusable, ou passer le repo en privé.

## Architecture des vidéos

Les vidéos ne vont **pas** dans le repo (limite 100 Mo/fichier sur GitHub).
Elles vivent sur R2 et sont servies en direct par `<video>` natif :

```html
<video autoplay muted loop playsinline preload="metadata"
       poster="assets/reel-akai-poster.jpg">
  <source src="https://videos.lilanarinx.com/reel-akai-sushi.mp4" type="video/mp4">
</video>
```

Aucune iframe, aucun player tiers, aucune pub.

## Structure

Racine volontairement nue : **que des dossiers**, sauf les deux fichiers qui
doivent y rester (`index.html` est la page servie par Cloudflare Pages dont
l'output directory est `/` ; `README.md` est la page d'accueil du repo GitHub).

```
.
├── index.html          Le site — doit rester à la racine (Pages)
├── README.md           Cette page — doit rester à la racine (GitHub)
│
├── assets/             Images web optimisées — SEUL dossier média versionné
├── docs/               DEPLOY.md · PUSH.md · MEDIA.md
├── scripts/            PUSH.command (double-clic Finder)
│
├── media/              ⛔ gitignoré (~985 Mo) — reste sur le Mac
│   ├── photos/         76 visuels du brief, rangés par section
│   └── videos/         11 vidéos → vont sur Cloudflare R2
│
└── _sources/           ⛔ gitignoré (~993 Mo) — reste sur le Mac
    ├── brief/          le docx de départ
    ├── images-vrac/    6 jpegs à trier
    ├── CV Lila Narinx.pdf
    └── wetransfer_….zip
```

Le détail de chaque dossier `media/` est dans **`docs/MEDIA.md`**.

## Mise à jour

Voir `docs/PUSH.md`. En résumé :

```bash
git add -A && git commit -m "message" && git push origin main
```

→ Cloudflare Pages redéploie automatiquement en 1-2 minutes.
