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
import hashlib
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
    "campagne-360": IMG / "76.webp",   # la mise en situation plutôt qu'une page de dossier
    "reseaux-sociaux": IMG / "79.webp",
    "sites-web": IMG / "75.webp",     # mockup Veyras : plus lisible qu'une capture rognée
    "photo": IMG / "40.webp",
    "video": POSTERS / "mockup-iphone-poche.webp",   # repli si la vidéo ne charge pas
    "redaction": IMG / "94.webp",
    "graphisme": IMG / "92.webp",
    "intelligence-artificielle": IMG / "96.webp",
}

def empreinte(chemin):
    """8 caractères tirés du contenu du fichier — sert de numéro de version
    dans l'URL (?v=…) pour que navigateurs et CDN rechargent après une modif."""
    try:
        return hashlib.md5(Path(chemin).read_bytes()).hexdigest()[:8]
    except Exception:
        return "0"


V_CSS = empreinte("assets/css/site.css")
V_JS = empreinte("assets/js/site.js")

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
# Combien de tuiles par rangée (sur 6 colonnes) selon l'orientation.
# La largeur vient de la FORME de l'image, jamais de sa position dans la
# liste : deux visuels de même format ont donc toujours la même taille.
PAR_RANGEE = {"tres-haut": 3, "haut": 3, "carre": 3, "large": 2, "banniere": 1}
# cas d'un visuel seul dans sa famille : on ne l'étale pas sur 6 colonnes
UNIQUE     = {"tres-haut": 2, "haut": 3, "carre": 3, "large": 4, "banniere": 6}


def famille(w, h):
    r = w / h
    if r >= 2.2: return "banniere"
    if r >= 1.2: return "large"
    if r >= .9:  return "carre"
    if r >= .6:  return "haut"
    return "tres-haut"


def media_html(m, titre_prod, span, pos=0):
    if m["type"] == "image":
        n = m["n"]
        src, plein = IMG / f"{n}.webp", IMG / f"{n}@full.webp"
        if not src.exists():
            print(f"   ⚠️  visuel {n} absent — ignoré")
            return ""
        w, h = taille(src)
        # numéro de POSITION, pas le numéro interne du brief
        alt = f"{titre_prod}, visuel {pos}" if pos else titre_prod
        contenir = " vignette--contenir" if famille(w, h) == "banniere" else ""
        large = " large" if (w / h) >= 1.2 or span >= 4 else ""
        return (
            f'<button class="vignette monte{contenir}{large}" type="button" '
            f'data-plein="{plein.as_posix()}" data-alt="{e(alt)}" '
            f'style="--r:{w}/{h};--s:{span}">'
            f'<img src="{src.as_posix()}" alt="{e(alt)}" width="{w}" height="{h}" '
            f'loading="lazy" decoding="async"></button>'
        )
    f = m["f"]
    poster = POSTERS / f"{f}.webp"
    pw, ph = taille(poster) if poster.exists() else (9, 16)
    att_poster = f' poster="{poster.as_posix()}"' if poster.exists() else ""
    att_debut = f' data-debut="{m["debut"]}"' if m.get("debut") else ""
    large = " large" if (pw / ph) >= 1.2 or span >= 4 else ""
    return (
        f'<div class="clip monte{large}" style="--r:{pw}/{ph};--s:{span}">'
        f'<video data-f="{e(f)}"{att_debut}{att_poster} muted loop playsinline preload="none" '
        f'width="{pw}" height="{ph}" tabindex="0" aria-label="{e(titre_prod)}"></video>'
        # aucune surcouche : ni bouton son, ni agrandir, ni durée.
        # Un clic sur la vidéo l'ouvre en grand, avec le son.
        f'</div>'
    )


def dims(m):
    if m["type"] == "image":
        return taille(IMG / f'{m["n"]}.webp')
    p = POSTERS / f'{m["f"]}.webp'
    return taille(p) if p.exists() else (9, 16)


def collage_html(medias, titre_prod, depart=0):
    if not medias:
        return ""
    fams = [famille(*dims(m)) for m in medias]
    tuiles, pos = [], depart
    for i, m in enumerate(medias):
        fam = fams[i]
        combien = fams.count(fam)
        if combien <= 1:
            span = UNIQUE[fam]
        else:
            # autant que possible par rangée, sans jamais dépasser le nombre
            # d'images de cette famille (2 visuels → 2 par rangée, pas 3)
            span = 6 // min(PAR_RANGEE[fam], combien)
        suivant = pos + 1 if m["type"] == "image" else pos
        t = media_html(m, titre_prod, span, suivant)
        if t:
            tuiles.append(t)
            pos = suivant
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
    if p.get("liens"):
        g.append('<p class="prod__liens">')
        for libelle, href in p["liens"]:
            g.append(
                f'<a href="{e(href)}" target="_blank" rel="noopener noreferrer">{e(libelle)}'
                f'<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                f'stroke-width="2.4" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg></a>')
        g.append("</p>")
    g.append("</div>")
    g.append('<div class="prod__medias">')
    nb = sum(1 for m in p["medias"] if m["type"] == "image")
    g.append(collage_html(p["medias"], p["titre"]))
    s = p.get("suite")
    if s:
        g.append('<div class="prod__suite">')
        g.append(f'<p class="prod__para monte">{e(s["texte"])}</p>')
        g.append(collage_html(s["medias"], p["titre"], depart=nb))
        g.append("</div>")
    g.append("</div></section>")
    return "".join(g)


# ─────────────────────────────────────────────────────────────────────
def coquille(titre_onglet, description, corps, actif=None, classe=""):
    I = C.IDENTITE
    liens = f'<a class="nav__lien-accueil" href="index.html"{" aria-current=\"page\"" if classe == "page-accueil" else ""}>Accueil</a>'
    liens += "".join(
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
<meta name="theme-color" content="#5b5617">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(titre_onglet)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="https://{e(I['domaine'])}/assets/img/76.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%235b5617'/><text x='50' y='50' dy='.35em' text-anchor='middle' font-family='Helvetica,Arial' font-weight='bold' font-size='54' fill='%23eeec83'>L</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..125,500..900&family=Instrument+Serif:ital@1&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v={V_CSS}">
</head>
<body class="{classe}">

<a class="saut-contenu" href="#contenu">Aller au contenu</a>

<nav class="nav" aria-label="Navigation principale">
  {f'<span class="nav__marque" aria-hidden="true" style="visibility:hidden">{e(I["nom"])}</span>' if classe == "page-accueil" else f'<a class="nav__marque" href="index.html"><span class="nav__fleche" aria-hidden="true">←</span>{e(I["nom"])}</a>'}
  <div class="nav__liens" id="menu-principal">{liens}</div>
  <a class="nav__contact" href="contact.html"{" aria-current=\"page\"" if actif == "contact" else ""}>Contact</a>
  <button class="nav__bascule" type="button" aria-expanded="false" aria-controls="menu-principal" aria-label="Menu"><span></span><span></span></button>
</nav>

<main id="contenu">
{corps}
</main>

<footer class="pied">
  <a class="pied__nom" href="index.html">{e(I['nom'])}
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
  </a>
  <p class="pied__coord">
    <a href="mailto:{e(I['email'])}">{e(I['email'])}</a>
    <a href="tel:{e(I['tel_lien'])}">{e(I['tel'])}</a>{('<a href="' + e(I['linkedin']) + '" target="_blank" rel="noopener">LinkedIn</a>') if I.get('linkedin') else ''}
  </p>
</footer>

<div class="boite" role="dialog" aria-modal="true" aria-label="Visionneuse" aria-hidden="true">
  <div class="boite__barre">
    <button class="boite__fermer" type="button" aria-label="Fermer"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
  </div>
  <div class="boite__scene"></div>
  <p class="boite__legende"></p>
  <button class="boite__fleche boite__fleche--prec" type="button" aria-label="Visuel précédent"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg></button>
  <button class="boite__fleche boite__fleche--suiv" type="button" aria-label="Visuel suivant"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg></button>
</div>

<script src="assets/js/site.js?v={V_JS}" defer></script>
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
    # on coupe à la fin de la PREMIÈRE PHRASE, pas au milieu d'une proposition
    coupe = texte.index(".", texte.index(cle)) + 1
    phrase, reste = texte[:coupe], texte[coupe:].strip().lstrip(" ")
    phrase_html = e(phrase).replace(cle, f"<em>{cle}</em>", 1)

    reperes = "".join(f"<div><dt>{e(t)}</dt><dd>{e(d)}</dd></div>" for t, d in C.REPERES)

    def visuel_tuile(r):
        # la tuile Vidéo joue un reel, muet et en boucle, comme dans les
        # rubriques — mais sans le clic-pour-agrandir : ici le clic doit
        # ouvrir la rubrique (le <a> englobant), pas la visionneuse.
        if r["id"] == "video":
            poster = COUVERTURES["video"]
            pw, ph = taille(poster) if poster.exists() else (4, 5)
            return (
                f'<video class="tuile__video" data-f="mockup-iphone-poche" '
                f'poster="{poster.as_posix()}" muted loop playsinline preload="none" '
                f'width="{pw}" height="{ph}" aria-hidden="true"></video>'
            )
        return img_tag(COUVERTURES[r["id"]], "", loading="lazy", decoding="async")

    tuiles = "".join(
        f'<a class="tuile monte" href="{page_de(r)}">'
        + '<span class="tuile__visuel">'
        + visuel_tuile(r)
        + f'</span><span class="tuile__corps"><span class="tuile__titre">{e(r["titre"])}</span><span class="tuile__fleche" aria-hidden="true">↗</span></span></a>'
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
    <div class="dedans">
      <div class="presentation__bloc monte">
        <h2 class="condense presentation__phrase">{phrase_html}</h2>
        <p class="presentation__texte">{e(reste)}</p>
      </div>
    </div>
  </section>

  <section class="bloc" id="productions" aria-label="{e(C.TITRE_PRODUCTIONS)}" style="padding-top:0">
    <div class="dedans">
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
      <h1 class="titre-geant rub__titre" style="--n:{len(r['titre'])}">{e(r['titre'])}</h1>
    </div>
  </header>

  {''.join(production_html(p, k) for k, p in enumerate(r['productions']))}

  <nav class="voisins" aria-label="Rubriques voisines">
    <a href="{page_de(prec)}"><span class="etq">Précédent</span> <strong>{e(prec['titre'])}</strong></a>
    <a href="{page_de(suiv)}"><span class="etq">Suivant</span> <strong>{e(suiv['titre'])}</strong></a>
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
        <p class="etq">Contact</p>
        <p class="fiche__nom">{e(I['nom'])}</p>
        <p class="fiche__role">{e(I['role'])}</p>
        <div class="fiche__liens">
          <a class="lien-contact" href="mailto:{e(I['email'])}">
            <span class="lien-contact__quoi">Écrire un mail</span>
            <span class="lien-contact__valeur">{e(I['email'])}</span>
            <span class="lien-contact__fleche" aria-hidden="true">↗</span>
          </a>
          <a class="lien-contact" href="tel:{e(I['tel_lien'])}">
            <span class="lien-contact__quoi">Appeler</span>
            <span class="lien-contact__valeur">{e(I['tel'])}</span>
            <span class="lien-contact__fleche" aria-hidden="true">↗</span>
          </a>
          {('<a class="lien-contact" href="' + e(I['linkedin']) + '" target="_blank" rel="noopener"><span class="lien-contact__quoi">LinkedIn</span><span class="lien-contact__valeur">Voir le profil</span><span class="lien-contact__fleche" aria-hidden="true">↗</span></a>') if I.get('linkedin') else ''}
        </div>
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
