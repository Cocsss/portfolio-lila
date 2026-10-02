# Index des médias

Correspondance entre la numérotation du brief (`_sources/brief/construction portfolio.docx`) et les fichiers rangés dans `media/`.

⚠️ `media/` et `_sources/` sont **gitignorés** (~2 Go, confidentialité
Takeaway, données personnelles du CV). Ils restent sur le Mac. Seules les
versions web optimisées et validées iront dans `assets/`.

## Visuels — `media/photos/`

| Brief | Dossier | Sujet |
|---|---|---|
| 1 → 8 | `01-campagne-360-takeaway/` | Campagne RP Takeaway.com (IHECS, grande distinction) — 🔒 **confidentiel** |
| 9 → 20 | `02-reseaux-sociaux/tribe-agency/` | Instagram La Stazione, FightClub, Vérigoud + compte agence (posts, stories, vues de feed) |
| 21 → 22 | `02-reseaux-sociaux/voyage-brazil-selection/` | Publications Instagram client Voyage Brazil Selection |
| 23 | `02-reseaux-sociaux/caerus/` | Publication Instagram asbl CAERUS (cofondatrice) |
| 24 → 31 | `02-reseaux-sociaux/venthone-consulting/` | Publications LinkedIn + nouvelle bannière |
| 32 | `02-reseaux-sociaux/evenement-fictif-ihecs/` | Projet fictif — communication événementielle |
| 33 → 38 | `03-sites-web-miege-veyras/` | Sites rebrandés et redesignés — clients Miège et Veyras |
| 39 → 45 | `04-photo/tribe-agency/` | Moodboards + photos emblématiques des shootings |
| 46 → 49 | `04-photo/vendredi-apero/` | Photos marque de boisson sans alcool « Vendredi Apér0% » |
| 50 → 51 | `05-redaction/newsletters-presse/` | Newsletter presse (database journalistes) — fête des mères |
| 52 → 53 | `05-redaction/blog-venthone/` | Articles de blog Venthone Consulting |
| 54 → 55 | `05-redaction/communiques-presse/` | Communiqués de presse (cours d'expression écrite IHECS) |
| 56 → 58 | `06-graphisme/takeaway-affiches/` | Affiches campagne Takeaway.com — 🔒 **confidentiel** |
| 59 → 60 | `06-graphisme/takeaway-dossiers-indesign/` | Dossiers de campagne InDesign — 🔒 **confidentiel** |
| 61 | `06-graphisme/pochette-cd/` | Pochette de CD (cours de graphisme IHECS) |
| 62 | `06-graphisme/affiche-cours/` | Affiche (cours de graphisme IHECS) |
| 63 → 66 | `06-graphisme/flyer-carte-visite/` | Flyer + carte de visite (projet médiatique IHECS) |
| 67 → 68 | `06-graphisme/evenement-fictif-ihecs/` | Logo + affiches événement fictif |
| 69 → 74 | `07-ia-cleopatre/` | Projet IA « Cléopâtre influenceuse » (Midjourney, Replicate, ElevenLabs, Suno, Runway, Heygen) |

## Vidéos — `media/videos/`

Elles ne peuvent pas aller sur GitHub (100 Mo max/fichier) → **Cloudflare R2**,
servies depuis `https://videos.lilanarinx.com/`.

| Fichier | Poids | Sujet |
|---|---|---|
| `tribe-agency/reel-akai-sushi.mp4` | 118 Mo | Reel AKAI Sushi |
| `tribe-agency/reel-cuisine-gazzosa.mp4` | 110 Mo | Reel cuisine Gazzosa |
| `tribe-agency/reel-cocktail-le-corbier.mov` | 74 Mo | Reel cocktail Le Corbier |
| `tribe-agency/reel-cocktail-framboise-delhaize.mov` | 80 Mo | Reel cocktail framboise / Delhaize Champagne |
| `tribe-agency/reel-post-it-ono.mov` | 55 Mo | Reel post-it Ono |
| `tribe-agency/reel-cuisine-ono.mov` | 73 Mo | Reel cuisine Ono |
| `vendredi-apero/apero-final.mp4` | 36 Mo | « Apéro final » — Vendredi Apér0% (Premiere Pro) |
| `vendredi-apero/poker-final.mp4` | 92 Mo | « Poker final » — Vendredi Apér0% (Premiere Pro) |
| `reportage-spear/projet-spear.mov` | 187 Mo | Reportage sur l'artiste bruxellois « Spear » (IHECS) |
| `erasmus-pub/pub-erasmus-1.mp4` | 12 Mo | Pub — cours « Audiovisual, Technology and Communication » (Erasmus) |
| `erasmus-pub/pub-erasmus-2.mp4` | 11 Mo | Pub — idem |

Total vidéos : **849 Mo** → à compresser avant R2 (voir `docs/DEPLOY.md`, section ffmpeg). Les reels Tribe Agency sont montés sur CapCut Pro, le reste sur
Premiere Pro.

## À faire avant d'intégrer

1. **Compresser les vidéos** en `.mp4` H.264 (les `.mov` surtout) → `docs/DEPLOY.md`
2. **Valider la confidentialité** des visuels Takeaway (1→8, 56→60) : le brief
   demande de ne pas les diffuser. Soit on les écarte du site public, soit on
   les met derrière une page protégée, soit Lila obtient l'accord.
3. **Trier `_sources/images-vrac/`** (6 jpegs non identifiés, dont peut-être un
   portrait à utiliser sur le site)
4. **Générer les versions web** dans `assets/` (redimensionnées, WebP)
