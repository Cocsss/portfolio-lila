# Déploiement — lilanarinx.com

Le repo GitHub est déjà créé et poussé. Le domaine `lilanarinx.com` est déjà
sur le compte Cloudflare. Il reste **3 étapes**, toutes dans le dashboard
Cloudflare (~10 minutes).

---

## 1. Créer le projet Cloudflare Pages

1. https://dash.cloudflare.com → **Workers & Pages** (menu de gauche)
2. **Create application** → onglet **Pages** → **Connect to Git**
3. Autorise Cloudflare sur GitHub si demandé, et **donne-lui accès au repo
   `portfolio-lila`** (bouton *Configure GitHub* → sélectionner le repo)
4. Sélectionne `portfolio-lila` → **Begin setup**
5. Config de build :
   - **Project name** : `portfolio-lila`
   - **Production branch** : `main`
   - **Framework preset** : `None`
   - **Build command** : *(vide)*
   - **Build output directory** : `/`
6. **Save and Deploy**
7. ~30 s plus tard le site est live sur `portfolio-lila.pages.dev`

---

## 2. Brancher le domaine

1. Toujours dans **Workers & Pages** → projet `portfolio-lila`
2. Onglet **Custom domains** → **Set up a custom domain**
3. Tape `lilanarinx.com` → **Continue** → **Activate domain**
4. Recommence pour `www.lilanarinx.com` (pour que les deux marchent)
5. Cloudflare crée le DNS + le SSL tout seul → actif en 1-5 minutes

⚠️ Si `lilanarinx.com` a déjà un enregistrement DNS qui pointe ailleurs
(ancien site, parking), Cloudflare propose de le remplacer — accepte.

---

## 3. Bucket R2 pour les vidéos

Les vidéos ne peuvent pas aller sur GitHub (100 Mo max par fichier).

### Créer le bucket
1. Dashboard → **R2**
2. Première fois : Cloudflare demande une **carte bancaire** même pour le plan
   gratuit (anti-abus). Pas débitée sous 10 Go.
3. **Create bucket** → nom : `lila-videos` → Location : Automatic → **Create**

### Le rendre public
1. Dans le bucket → onglet **Settings**
2. **Public access** → **Custom Domains** → **Connect Domain**
3. Tape `videos.lilanarinx.com` → Cloudflare configure le DNS + SSL (1-2 min)

### Uploader
1. Bucket → **Objects** → **Upload** → drag & drop les `.mp4`
2. Chaque fichier est alors dispo à
   `https://videos.lilanarinx.com/nomdufichier.mp4`

**Nommage** : minuscules, sans espaces ni accents.
`reel-akai-sushi.mp4`, `apero-final.mp4`, `projet-spear.mp4`…

**Convertir les `.mov` en `.mp4`** avant upload (bien plus léger) :

```bash
ffmpeg -i "Reel cocktail Le Corbier.mov" -vcodec libx264 -crf 23 \
       -preset slow -acodec aac -b:a 128k reel-cocktail-le-corbier.mp4
```

---

## 4. Brancher une vidéo dans le site

```html
<video class="reel" autoplay muted loop playsinline preload="metadata"
       poster="assets/reel-akai-poster.jpg">
  <source src="https://videos.lilanarinx.com/reel-akai-sushi.mp4" type="video/mp4">
</video>
```

Puis :

```bash
git add -A && git commit -m "branche vidéos R2" && git push origin main
```

---

## Workflow pour la suite

Voir `PUSH.md`. Chaque `git push origin main` redéploie le site.

---

## Coût

| Poste | Coût/an |
|---|---|
| Domaine `.com` (déjà payé) | ~9,80 € |
| Cloudflare Pages | 0 € |
| Cloudflare R2 (sous 10 Go) | 0 € |
| SSL, CDN, DNS | 0 € |

---

## Dépannage

- **"Pages build failed"** → build command vide, output directory `/`
- **Domaine inaccessible** → attendre 5-10 min (propagation DNS)
- **Vidéo ne charge pas** → vérifier Public access + custom domain du bucket ;
  tester l'URL directement dans un onglet
- **Repo invisible dans Cloudflare** → GitHub → Settings → Applications →
  Cloudflare Pages → donner accès à `portfolio-lila`
