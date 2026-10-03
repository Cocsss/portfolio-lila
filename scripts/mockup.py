#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mises en situation fabriquées à partir des visuels du portfolio.

Trois scènes, toutes carrées, sur le fond vert du site :

    tel      affiche + iPhone          → Campagne 360°
    affiche  une affiche seule, posée  → Graphisme
    feuilles plusieurs A4 en éventail  → Rédaction

Exemples :
    python3 scripts/mockup.py tel      --affiche 57 --ecran 7:100,215,352,663 --n 76
    python3 scripts/mockup.py affiche  --src 62 --n 78
    python3 scripts/mockup.py feuilles --src 54,55,52 --n 79

Une découpe s'écrit « 7:x0,y0,x1,y1 » : la zone prise dans le visuel 7.

MARGE DE SÉCURITÉ : les tuiles de l'accueil sont en 4/5 et rognent 160 px
de chaque côté d'un carré de 1600. Le contenu reste donc à l'intérieur
d'une zone utile de 1240 px, pour ne jamais être coupé.
"""
import os
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
os.chdir(RACINE)

from PIL import Image, ImageDraw, ImageFilter

IMG = Path("assets/img")

COTE = 1600
SUR  = 180                     # marge de sécurité (rognage 4/5 = 160 px)
UTILE = COTE - 2 * SUR         # 1240 px réellement exploitables

VERT  = (91, 86, 23)           # --vert du site
BEZEL = (38, 38, 41)           # châssis du téléphone
ACIER = (118, 118, 124)        # tranche métallique


# ─────────────────────────────────────────────────────────────────────
#  Outils
# ─────────────────────────────────────────────────────────────────────
def fond():
    """Le vert du site, avec un dégradé très léger pour ne pas être plat."""
    haut = tuple(min(255, c + 13) for c in VERT)
    bas = tuple(max(0, c - 11) for c in VERT)
    g = Image.new("RGB", (1, COTE))
    for y in range(COTE):
        t = y / COTE
        g.putpixel((0, y), tuple(round(h + (b - h) * t) for h, b in zip(haut, bas)))
    return g.resize((COTE, COTE))


def ombre(scene, boite, rayon, flou, opacite, decalage, teinte=(26, 24, 10)):
    couche = Image.new("L", scene.size, 0)
    x0, y0, x1, y1 = boite
    dx, dy = decalage
    ImageDraw.Draw(couche).rounded_rectangle(
        (x0 + dx, y0 + dy, x1 + dx, y1 + dy), rayon, fill=opacite)
    scene.paste(Image.new("RGB", scene.size, teinte), (0, 0),
                couche.filter(ImageFilter.GaussianBlur(flou)))


def arrondir(im, rayon):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1),
                                        rayon, fill=255)
    im = im.convert("RGBA")
    im.putalpha(m)
    return im


def ouvrir(spec):
    """« 57 » → le visuel 57 · « 7:x0,y0,x1,y1 » → une découpe dedans."""
    if ":" in spec:
        n, b = spec.split(":", 1)
        x0, y0, x1, y1 = (int(v) for v in b.split(","))
        return _fichier(n).crop((x0, y0, x1, y1))
    return _fichier(spec)


def _fichier(n):
    for c in (IMG / f"{n}@full.webp", IMG / f"{n}.webp", Path(n)):
        if c.exists():
            return Image.open(c).convert("RGB")
    raise SystemExit(f"introuvable : {n}")


def haut(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


def papier(im):
    """Un soupçon de relief : bord clair en haut, léger assombrissement en bas."""
    v = Image.new("L", (1, im.height))
    for y in range(im.height):
        t = y / max(1, im.height - 1)
        v.putpixel((0, y), round(128 + 16 * (1 - t) - 20 * t))
    voile = v.resize(im.size)
    clair = Image.new("RGB", im.size, (255, 255, 255))
    sombre = Image.new("RGB", im.size, (0, 0, 0))
    return Image.blend(Image.composite(clair, sombre, voile), im.convert("RGB"), .88)


# ─────────────────────────────────────────────────────────────────────
#  Le téléphone
# ─────────────────────────────────────────────────────────────────────
def telephone(ecran, hauteur):
    """iPhone moderne : angles très arrondis, tranche métallique,
    Dynamic Island, boutons latéraux, reflet diagonal sur la dalle."""
    ec = haut(ecran, hauteur)
    bord = max(10, round(hauteur * 0.013))          # liseré noir autour de la dalle
    pw, ph = ec.width + bord * 2, ec.height + bord * 2
    r_ext = round(pw * 0.138)

    tel = Image.new("RGBA", (pw + 8, ph + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(tel)

    # tranche métallique, puis châssis noir légèrement plus petit
    d.rounded_rectangle((0, 0, pw + 7, ph + 7), r_ext + 3, fill=ACIER + (255,))
    d.rounded_rectangle((4, 4, pw + 3, ph + 3), r_ext, fill=BEZEL + (255,))

    tel.paste(arrondir(ec, round(r_ext * 0.86)), (4 + bord, 4 + bord),
              arrondir(ec, round(r_ext * 0.86)))

    # Dynamic Island
    iw, ih = round(pw * 0.30), round(hauteur * 0.032)
    ix = 4 + (pw - iw) // 2
    iy = 4 + bord + round(hauteur * 0.016)
    d.rounded_rectangle((ix, iy, ix + iw, iy + ih), ih // 2, fill=(12, 12, 14, 255))

    # boutons latéraux
    bl = round(hauteur * 0.004)
    d.rounded_rectangle((0, round(ph * 0.20), bl + 2, round(ph * 0.26)), bl, fill=ACIER + (255,))
    d.rounded_rectangle((0, round(ph * 0.30), bl + 2, round(ph * 0.40)), bl, fill=ACIER + (255,))
    d.rounded_rectangle((pw + 5, round(ph * 0.26), pw + 7, round(ph * 0.38)), bl, fill=ACIER + (255,))

    # reflet diagonal discret
    refl = Image.new("L", tel.size, 0)
    ImageDraw.Draw(refl).polygon(
        [(0, round(ph * .62)), (round(pw * .62), 0), (round(pw * .96), 0),
         (0, round(ph * .95))], fill=30)
    refl = refl.filter(ImageFilter.GaussianBlur(26))
    masque = Image.new("L", tel.size, 0)
    ImageDraw.Draw(masque).rounded_rectangle((4, 4, pw + 3, ph + 3), r_ext, fill=255)
    refl = Image.composite(refl, Image.new("L", tel.size, 0), masque)
    tel.paste(Image.new("RGB", tel.size, (255, 255, 255)), (0, 0), refl)
    return tel


# ─────────────────────────────────────────────────────────────────────
#  Scènes
# ─────────────────────────────────────────────────────────────────────
def scene_tel(spec_affiche, spec_ecran):
    s = fond()
    aff = papier(haut(ouvrir(spec_affiche), 760))
    tel = telephone(ouvrir(spec_ecran), 820)

    total = aff.width + tel.width
    ecart = (UTILE - total) // 3
    ax = SUR + ecart
    px = ax + aff.width + ecart
    ay = (COTE - aff.height) // 2 + 26
    py = (COTE - tel.height) // 2

    ombre(s, (ax, ay, ax + aff.width, ay + aff.height), 4, 34, 84, (8, 20))
    s.paste(aff, (ax, ay))
    ombre(s, (px + 6, py + 6, px + tel.width - 6, py + tel.height - 6),
          round(tel.width * .14), 42, 104, (12, 26))
    s.paste(tel, (px, py), tel)
    return s


def scene_affiche(spec):
    """Une affiche seule, posée bien au centre."""
    s = fond()
    aff = papier(haut(ouvrir(spec), 1120))
    if aff.width > UTILE:
        aff = aff.resize((UTILE, round(aff.height * UTILE / aff.width)), Image.LANCZOS)
    ax = (COTE - aff.width) // 2
    ay = (COTE - aff.height) // 2
    ombre(s, (ax, ay, ax + aff.width, ay + aff.height), 4, 44, 96, (10, 26))
    s.paste(aff, (ax, ay))
    return s


def scene_feuilles(specs):
    """Des A4 en éventail, la dernière bien à plat devant."""
    s = fond()
    pages = [papier(haut(ouvrir(x), 980)) for x in specs][:3]
    angles = [-7, 4, 0][-len(pages):]
    decales = [(-150, -34), (140, -14), (0, 46)][-len(pages):]

    for page, angle, (dx, dy) in zip(pages, angles, decales):
        p = page.convert("RGBA")
        if angle:
            p = p.rotate(angle, expand=True, resample=Image.BICUBIC)
        x = (COTE - p.width) // 2 + dx
        y = (COTE - p.height) // 2 + dy
        ombre(s, (x + 14, y + 14, x + p.width - 14, y + p.height - 14), 6, 36, 88, (8, 20))
        s.paste(p, (x, y), p)
    return s


# ─────────────────────────────────────────────────────────────────────
def enregistrer(im, n):
    for suf, large, q in (("", 1000, 80), ("@full", 1800, 82)):
        c = im.copy()
        r = large / max(c.size)
        if r < 1:
            c = c.resize((round(c.width * r), round(c.height * r)), Image.LANCZOS)
        c.convert("RGB").save(IMG / f"{n}{suf}.webp", "WEBP", quality=q, method=6)
    a = (IMG / f"{n}.webp").stat().st_size // 1024
    b = (IMG / f"{n}@full.webp").stat().st_size // 1024
    print(f"  assets/img/{n}.webp  {a} Ko   ·   {n}@full.webp  {b} Ko")


def opt(nom, defaut=None):
    return sys.argv[sys.argv.index(nom) + 1] if nom in sys.argv else defaut


def prochain():
    n = 0
    for f in IMG.glob("*.webp"):
        t = f.stem.replace("@full", "")
        if t.isdigit():
            n = max(n, int(t))
    return n + 1


if __name__ == "__main__":
    quoi = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "tel"
    n = int(opt("--n", prochain()))
    if quoi == "tel":
        im = scene_tel(opt("--affiche", "57"), opt("--ecran", "7:100,215,352,663"))
    elif quoi == "affiche":
        im = scene_affiche(opt("--src", "62"))
    elif quoi == "feuilles":
        im = scene_feuilles(opt("--src", "54,55,52").split(","))
    else:
        raise SystemExit("scène inconnue : tel | affiche | feuilles")
    print(f"{quoi} — carré {COTE}×{COTE}, contenu dans les {UTILE} px sûrs  →  visuel {n}")
    enregistrer(im, n)
