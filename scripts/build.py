#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère le site à partir de scripts/content.py et des visuels de assets/img/.

    python3 scripts/build.py

Produit :
    index.html                  accueil
    campagne-360.html, …        une page par rubrique
    404.html

Textes : scripts/content.py · style : assets/css/site.css · JS : assets/js/site.js
"""
import html
import os
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
os.chdir(RACINE)
sys.path.insert(0, str(RACINE / "scripts"))

from PIL import Image
import content as C

IMG = Path("assets/img")
POSTERS = IMG / "posters"

# Visuel de couverture de chaque page (numéro du brief, ou poster vidéo).
COUVERTURES = {
    "accueil": IMG / "42.webp",
    "campagne-360": IMG / "56.webp",
    "reseaux-sociaux": IMG / "15.webp",
    "sites-web": IMG / "33.webp",
    "photo": IMG / "40.webp",
    "video": POSTERS / "reel-cuisine-gazzosa.webp",
    "redaction": IMG / "51.webp",
    "graphisme": IMG / "61.webp",
    "intelligence-artificielle": IMG / "71.webp",
}

_tailles = {}


def taille(p):
    p = str(p)
    if p not in _tailles:
        try:
            with Image.open(p) as im:
                _tailles[p] = im.size
        except Exception:
            _tailles[p] = (3, 4)
    return _tailles[p]


def e(t):
    return html.escape(str(t), quote=True)


def page_de(r):
    return f'{r["id"]}.html'


def compte_medias(r):
    return sum(len(p["medias"]) + len(p.get("suite", {}).get("medias", []))
               for p in r["productions"])


# ─────────────────────────────────────────────────────────────────────
#  Collage : chaque tuile reçoit une largeur (en colonnes sur 6) selon
#  son orientation, en suivant un motif qui se répète — d'où l'aspect
#  « images dispersées » des références, sans rien forcer au recadrage.
# ─────────────────────────────────────────────────────────────────────
MOTIFS = {
    "tres-haut": [2, 2, 2, 2, 2, 2],         # stories, captures d'écran
    "haut":      [2, 2, 2, 3, 3, 2, 4, 2],   # affiches, posts 4:5, pages A4
    "carre":     [3, 3, 2, 2, 2],
    "large":     [6, 3, 3],                  # captures de sites, double pages
    "banniere":  [6],
}


def famille(w, h):
    r = w / h
    if r >= 2.2: return "banniere"
    if r >= 1.2: return "large"
    if r >= .9:  return "carre"
    if r >= .6:  return "haut"
    return "tres-haut"


def media_html(m, titre_prod, span):
    if m["type"] == "image":
        n = m["n"]
        src, plein = IMG / f"{n}.webp", IMG / f"{n}@full.webp"
        if not src.exists():
            print(f"   ⚠️  visuel {n} absent — ignoré")
            return ""
        w, h = taille(src)
        alt = f"{titre_prod}, visuel {n}"
        contenir = " vignette--contenir" if famille(w, h) == "banniere" else ""
        large = " large" if span >= 4 else ""
        return (
            f'<button class="vignette{contenir}{large}" type="button" data-n="{n}" '
            f'data-plein="{plein.as_posix()}" data-alt="{e(alt)}" '
            f'style="--r:{w}/{h};--s:{span}">'
            f'<img src="{src.as_posix()}" alt="{e(alt)}" width="{w}" height="{h}" '
            f'loading="lazy" decoding="async"></button>'
        )
    f = m["f"]
    poster = POSTERS / f"{f}.webp"
    pw, ph = taille(poster) if poster.exists() else (9, 16)
    att_poster = f' poster="{poster.as_posix()}"' if poster.exists() else ""
    large = " large" if span >= 4 else ""
    return (
        f'<div class="clip{large}" style="--r:{pw}/{ph};--s:{span}">'
        f'<video data-f="{e(f)}"{att_poster} muted loop playsinline preload="none" '
        f'width="{pw}" height="{ph}" aria-label="{e(f.replace("-", " "))}"></video>'
        f'<button class="clip__son" type="button" aria-label="Activer le son"></button>'
        f'<span class="clip__duree" aria-hidden="true"></span></div>'
    )


def dims(m):
    if m["type"] == "image":
        return taille(IMG / f'{m["n"]}.webp')
    p = POSTERS / f'{m["f"]}.webp'
    return taille(p) if p.exists() else (9, 16)


def collage_html(medias, titre_prod):
    if not medias:
        return ""
    fams = [famille(*dims(m)) for m in medias]
    dominante = max(set(fams), key=fams.count)
    motif = MOTIFS[dominante]
    tuiles = []
    for i, m in enumerate(medias):
        fam = fams[i]
        span = 6 if fam == "banniere" else motif[i % len(motif)]
        if len(medias) == 1 and fam != "banniere":
            span = 4 if fam == "large" else 3
        if fam == "large" and span < 3:
            span = 3
        t = media_html(m, titre_prod, span)
        if t:
            tuiles.append(t)
    return f'<div class="collage">{"".join(tuiles)}</div>'


# ─────────────────────────────────────────────────────────────────────
def production_html(p, i):
    g = [f'<section class="prod" aria-labelledby="p{i}">',
         '<div class="prod__texte monte">',
         f'<h2 class="prod__titre" id="p{i}">{e(p["titre"])}</h2>']
    for cle in ("texte", "texte2"):
        if p.get(cle):
            g.append(f'<p class="prod__para">{e(p[cle])}</p>')
    if p.get("note"):
        g.append(f'<p class="prod__note"><strong>Confidentiel.</strong> {e(p["note"])}</p>')
    if p.get("ressources"):
        g.append(f'<p class="etq etq--jaune prod__ress">{e(p["ressources"])}</p>')
    g.append("</div>")
    g.append('<div class="prod__medias monte">')
    g.append(collage_html(p["medias"], p["titre"]))
    s = p.get("suite")
    if s:
        g.append('<div class="prod__suite">')
        g.append(f'<p class="prod__para">{e(s["texte"])}</p>')
        if s.get("ressources"):
            g.append(f'<p class="etq etq--jaune" style="margin-bottom:1rem">{e(s["ressources"])}</p>')
        g.append(collage_html(s["medias"], p["titre"]))
        g.append("</div>")
    g.append("</div></section>")
    return "".join(g)


# ─────────────────────────────────────────────────────────────────────
def coquille(titre_onglet, description, corps, actif=None, classe=""):
    I = C.IDENTITE
    liens = "".join(
        f'<a href="{page_de(r)}"' + (' aria-current="page"' if r["id"] == actif else "")
        + f'>{e(r["titre"])}</a>' for r in C.RUBRIQUES)
    liens += f'<a class="nav__lien-contact" href="contact.html"{" aria-current=\"page\"" if actif == "contact" else ""}>Contact</a>'
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre_onglet)}</title>
<meta name="description" content="{e(description)}">
<meta name="author" content="{e(I['nom'])}">
<meta name="theme-color" content="#4a1c70">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(titre_onglet)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="https://{e(I['domaine'])}/assets/img/portrait.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%234a1c70'/><text x='50' y='50' dy='.35em' text-anchor='middle' font-family='Helvetica,Arial' font-weight='bold' font-size='54' fill='%23d9d921'>L</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..125,500..900&family=Instrument+Serif:ital@1&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body class="{classe}">

<a class="saut-contenu" href="#contenu">Aller au contenu</a>

<nav class="nav" aria-label="Navigation principale">
  {"<span class=\"nav__marque\" aria-hidden=\"true\"></span>" if classe == "page-accueil" else f'<a class="nav__marque" href="index.html">{e(I["nom"])}</a>'}
  <div class="nav__liens">{liens}</div>
  <a class="nav__contact" href="contact.html"{" aria-current=\"page\"" if actif == "contact" else ""}>Contact</a>
  <button class="nav__bascule" type="button" aria-expanded="false" aria-label="Ouvrir le menu"><span></span><span></span></button>
</nav>

<main id="contenu">
{corps}
</main>

<footer class="pied">
  <p class="pied__nom">{e(I['nom'])}</p>
  <p class="pied__coord">
    <a href="mailto:{e(I['email'])}">{e(I['email'])}</a>
    <a href="tel:{e(I['tel_lien'])}">{e(I['tel'])}</a>{('<a href="' + e(I['linkedin']) + '" target="_blank" rel="noopener">LinkedIn</a>') if I.get('linkedin') else ''}
  </p>
</footer>

<div class="boite" role="dialog" aria-modal="true" aria-label="Visionneuse" aria-hidden="true">
  <div class="boite__barre">
    <p class="boite__compte"></p>
    <button class="boite__fermer" type="button" aria-label="Fermer"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
  </div>
  <div class="boite__scene"></div>
  <p class="boite__legende"></p>
  <button class="boite__fleche boite__fleche--prec" type="button" aria-label="Visuel précédent"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg></button>
  <button class="boite__fleche boite__fleche--suiv" type="button" aria-label="Visuel suivant"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg></button>
</div>

<script src="assets/js/site.js" defer></script>
</body>
</html>
"""


def img_tag(p, alt, **attrs):
    w, h = taille(p)
    extra = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    return f'<img src="{Path(p).as_posix()}" alt="{e(alt)}" width="{w}" height="{h}" {extra}>'


# ─────────────────────────────────────────────────────────────────────
def accueil():
    I = C.IDENTITE
    # La première phrase du texte de présentation, mise en grand ; le reste suit.
    texte = C.PRESENTATION["texte"]
    # coupe après « la création » : la suite du texte continue en corps,
    # sans rien ajouter ni retirer au docx.
    cle = "la création"
    coupe = texte.index(cle) + len(cle)
    phrase, reste = texte[:coupe], texte[coupe:].strip().lstrip(" ")
    phrase_html = e(phrase).replace(cle, f"<em>{cle}</em>", 1)

    reperes = "".join(f"<div><dt>{e(t)}</dt><dd>{e(d)}</dd></div>" for t, d in C.REPERES)
    tuiles = "".join(
        f'<a class="tuile monte" href="{page_de(r)}">'
        + img_tag(COUVERTURES[r["id"]], r["titre"], loading="lazy", decoding="async")
        + f'<span class="tuile__corps"><span class="tuile__titre">{e(r["titre"])}</span>'
        f'<span class="tuile__compte">{compte_medias(r)} contenus</span></span></a>'
        for i, r in enumerate(C.RUBRIQUES))

    corps = f"""
  <section class="hero" aria-label="Accueil">
    <div class="dedans">
      <h1 class="titre-geant hero__nom"><span>Lila</span> <span>Narinx</span></h1>
      <div class="hero__bas">
        <p class="hero__role">{e(I['role'])}</p>
      </div>
    </div>
  </section>

  <section class="bloc" id="presentation" aria-label="{e(C.PRESENTATION['titre'])}">
    <div class="dedans presentation">
      <div class="monte">
        <p class="etq" style="margin-bottom:1.4rem">{e(C.PRESENTATION['titre'])}</p>
        <h2 class="condense presentation__phrase">{phrase_html}</h2>
        <p class="presentation__texte">{e(reste)}</p>
      </div>
      <div class="presentation__portrait monte">
        {img_tag(C.PRESENTATION['portrait'], 'Portrait de ' + I['nom'], loading='lazy', decoding='async')}
      </div>
    </div>
  </section>

  <section class="bloc" id="productions" aria-label="{e(C.TITRE_PRODUCTIONS)}" style="padding-top:0">
    <div class="dedans">
      <div class="index__tete monte">
        <p class="etq">{e(C.TITRE_PRODUCTIONS)}</p>
      </div>
      <div class="index">{tuiles}</div>
    </div>
  </section>

"""
    return coquille(f"{I['nom']} · Portfolio",
                    f"Portfolio de {I['nom']} : {I['role'].lower()}.",
                    corps, classe="page-accueil")


# ─────────────────────────────────────────────────────────────────────
def page_rubrique(r, i):
    n = len(C.RUBRIQUES)
    prec, suiv = C.RUBRIQUES[(i - 1) % n], C.RUBRIQUES[(i + 1) % n]
    corps = f"""
  <header class="rub__tete" aria-label="{e(r['titre'])}">
    <div>
      <h1 class="titre-geant rub__titre">{e(r['titre'])}</h1>
    </div>
  </header>

  {''.join(production_html(p, k) for k, p in enumerate(r['productions']))}

  <nav class="voisins" aria-label="Rubriques voisines">
    <a href="{page_de(prec)}"><span class="etq">Précédent</span><strong>{e(prec['titre'])}</strong></a>
    <a href="{page_de(suiv)}"><span class="etq">Suivant</span><strong>{e(suiv['titre'])}</strong></a>
  </nav>
"""
    desc = r["productions"][0].get("texte") or f"{r['titre']}, portfolio de {C.IDENTITE['nom']}."
    return coquille(f"{r['titre']} · {C.IDENTITE['nom']}", desc[:300], corps,
                    actif=r["id"], classe="page-rubrique")


def page_contact():
    I = C.IDENTITE
    corps = f"""
  <section class="bloc contact contact--page" aria-label="Contact">
    <div class="dedans">
      <div class="fiche monte">
        <div class="fiche__tete">
          <p class="etq">Contact</p>
          <p class="fiche__nom">{e(I['nom'])}</p>
          <p class="fiche__role">{e(I['role'])}</p>
        </div>
        <dl class="fiche__liste">
          <div><dt>Email</dt><dd><a href="mailto:{e(I['email'])}">{e(I['email'])}</a></dd></div>
          <div><dt>Téléphone</dt><dd><a href="tel:{e(I['tel_lien'])}">{e(I['tel'])}</a></dd></div>
          {('<div><dt>LinkedIn</dt><dd><a href="' + e(I['linkedin']) + '" target="_blank" rel="noopener">Voir le profil</a></dd></div>') if I.get('linkedin') else ''}
        </dl>
      </div>
    </div>
  </section>
"""
    return coquille(f"Contact · {I['nom']}", f"Contacter {I['nom']}.", corps,
                    actif="contact", classe="page-contact")


def page_404():
    corps = """
  <section class="bloc" style="min-height:100svh;display:grid;align-content:center">
    <div class="dedans">
      <p class="etq">Erreur 404</p>
      <h1 class="titre-geant" style="font-size:clamp(2.6rem,11vw,9rem);color:var(--jaune);margin:.6rem 0 1.6rem">Page introuvable</h1>
      <a class="nav__contact" href="index.html">Retour à l'accueil</a>
    </div>
  </section>
"""
    return coquille("Page introuvable · Lila Narinx", "Page introuvable.", corps)


if __name__ == "__main__":
    pages = {"index.html": accueil(), "contact.html": page_contact(), "404.html": page_404()}
    for i, r in enumerate(C.RUBRIQUES):
        pages[page_de(r)] = page_rubrique(r, i)
    tv = tc = 0
    for nom, contenu in pages.items():
        Path(nom).write_text(contenu, encoding="utf8")
        tv += contenu.count('class="vignette')
        tc += contenu.count('<video ')
        print(f"  {nom:<32} {len(contenu) / 1024:>5.0f} Ko")
    print(f"\n✅ {len(pages)} pages · {tv} visuels · {tc} vidéos")
