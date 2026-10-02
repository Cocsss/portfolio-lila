# 🚀 Push en ligne — lilanarinx.com

## TL;DR — 3 commandes

```bash
cd ~/Desktop/"Portfolio LIla"
git add -A && git commit -m "update"
git push origin main
```

Une fois `git push origin main` lancé, **Cloudflare Pages rebuild le site
automatiquement** (~1-2 minutes) et lilanarinx.com est à jour.

Ou plus simple : **double-clique `scripts/PUSH.command`** dans le Finder.

---

## Liens utiles

| Quoi | Où |
|---|---|
| 🌐 Site live | https://lilanarinx.com |
| ⚙️ Dashboard Cloudflare | https://dash.cloudflare.com |
| 📦 Repo GitHub | https://github.com/Cocsss/portfolio-lila |
| 🎬 Bucket R2 (vidéos) | Dashboard Cloudflare → R2 |
| 🔧 Pages (build logs) | Workers & Pages → portfolio-lila |

---

## Suivi du déploiement

1. Va sur https://dash.cloudflare.com
2. **Workers & Pages** → projet `portfolio-lila`
3. Onglet **Deployments** → le build en cours (🟡 Building → 🟢 Success)
4. Quand c'est vert, actualise lilanarinx.com (vide le cache : `Cmd+Shift+R`)

---

## Si ça push pas

```bash
# Vérifie la branche
git branch --show-current    # doit être "main"

# Rien à commiter ?
git status
```

---

## Checklist avant de push

- [ ] Testé en local (ouvre `index.html` dans Safari/Chrome)
- [ ] **Aucun visuel Takeaway.com confidentiel ajouté** (repo public)
- [ ] Pas de vidéo dans le repo (elles vont sur R2)
- [ ] Pas de fichier sensible (CV, `.env`, clés API…)
- [ ] Message de commit explicite
- [ ] Push sur **`main`**
