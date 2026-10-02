# Portfolio — Lila Narinx

Site portfolio de Lila Narinx (social media & création de contenu), hébergé
gratuitement sur Cloudflare Pages, vidéos servies direct depuis Cloudflare R2.

Live : https://lilanarinx.com

## Stack

- **Site** : `index.html` (vanilla HTML/CSS/JS, zéro dépendance)
- **Hébergement site** : Cloudflare Pages (gratuit, bande passante illimitée)
- **Hébergement vidéo** : Cloudflare R2 (10 Go gratuits, egress gratuit)
- **Domaine** : Cloudflare (déjà sur le compte)

## État actuel

`index.html` est une **page d'attente**. Le portfolio complet est à construire
à partir du brief (`construction portfolio.docx`, gardé en local) qui décrit
8 sections et 76 contenus :

| Section | Contenus |
|---|---|
| Campagne 360° — RP Takeaway.com (IHECS) | 1 à 8 |
| Réseaux sociaux — Tribe Agency, Voyage Brazil Selection, CAERUS, Venthone | 9 à 32 |
| Sites web — Miège, Veyras | 33 à 38 |
| Photo — Tribe Agency, Vendredi Apér0% | 39 à 49 |
| Rédaction — newsletters presse, blog, communiqués | 50 à 55 |
| Graphisme — affiches Takeaway, dossiers InDesign, pochette CD, flyers, logo | 56 à 68 |
| Intelligence artificielle — projet Cléopâtre influenceuse | 69 à 74 |
| Vidéo — +50 reels Tribe Agency, Vendredi Apér0%, reportage SPEAR, pubs Erasmus | 75 à 76 + reels |

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

```
.
├── index.html              Site
├── assets/                 Images du site (visuels triés, posters vidéo)
├── media/
│   ├── photos/             Photos sources utilisées dans le site
│   └── videos/             (gitignoré — vit sur R2)
├── PUSH.md                 Comment mettre le site à jour
├── DEPLOY.md               Mise en place Cloudflare Pages + R2
└── README.md
```

## Mise à jour

Voir `PUSH.md`. En résumé :

```bash
git add -A && git commit -m "message" && git push origin main
```

→ Cloudflare Pages redéploie automatiquement en 1-2 minutes.
