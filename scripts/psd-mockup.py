#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Place un visuel du portfolio dans un mockup PSD du commerce.

Le PSD contient un calque « objet dynamique » qui sert d'emplacement.
On lit sa zone de placement, on y projette l'image, puis on recompose
par-dessus les calques qui doivent rester au-dessus (ombres, cadre,
reflets plastique…) pour garder le rendu réaliste.

    .venv-psd/bin/python scripts/psd-mockup.py \
        --psd "psd/…/Poster-Board-Mockup.psd" \
        --calque "POSTER - PLACE YOUR DESIGN" \
        --src 57 --n 77

    --lister   affiche la structure du PSD et s'arrête
"""
import os
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
os.chdir(RACINE)

from PIL import Image, ImageDraw, ImageFilter
from psd_tools import PSDImage
from psd_tools.constants import Tag

IMG = Path("assets/img")

sys.path.insert(0, str(RACINE / "scripts"))


def ouvrir(spec):
    """« 57 » → le visuel 57 · « 7:x0,y0,x1,y1 » → une découpe dedans."""
    if ":" in spec and not Path(spec).exists():
        n, b = spec.split(":", 1)
        x0, y0, x1, y1 = (int(v) for v in b.split(","))
        return _fichier(n).crop((x0, y0, x1, y1))
    return _fichier(spec)


def _fichier(n):
    for c in (IMG / f"{n}@full.webp", IMG / f"{n}.webp", Path(n)):
        if c.exists():
            return Image.open(c).convert("RGB")
    raise SystemExit(f"introuvable : {n}")


def tous_les_calques(racine):
    for l in racine:
        yield l
        if l.is_group():
            yield from tous_les_calques(l)


def lister(psd, prof=0, c=None):
    for l in (c if c is not None else psd):
        marque = "  ← EMPLACEMENT" if type(l).__name__ == "SmartObjectLayer" else ""
        print("  " * prof + f"· {l.name}{marque}")
        if l.is_group():
            lister(psd, prof + 1, l)


def coins(calque):
    """Les 4 coins du placement, dans l'ordre : haut-gauche, haut-droit,
    bas-droit, bas-gauche. Souvent un rectangle droit, parfois un
    quadrilatère incliné (objet photographié de biais)."""
    d = (calque.tagged_blocks.get_data(Tag.PLACED_LAYER2)
         or calque.tagged_blocks.get_data(Tag.PLACED_LAYER1))
    t = [float(v) for v in d.transform]
    return list(zip(t[0::2], t[1::2]))


def est_droit(q, tol=1.5):
    return (abs(q[0][1] - q[1][1]) < tol and abs(q[2][1] - q[3][1]) < tol
            and abs(q[0][0] - q[3][0]) < tol and abs(q[1][0] - q[2][0]) < tol)


def homographie(dest, src):
    """Coefficients PIL : pour chaque pixel de destination, où aller
    chercher la couleur dans l'image source."""
    import numpy as np
    A, B = [], []
    for (xd, yd), (xs, ys) in zip(dest, src):
        A.append([xd, yd, 1, 0, 0, 0, -xs * xd, -xs * yd])
        A.append([0, 0, 0, xd, yd, 1, -ys * xd, -ys * yd])
        B += [xs, ys]
    return np.linalg.solve(np.array(A, dtype=float), np.array(B, dtype=float))


def projeter(image, quad, taille_canevas):
    """Projette l'image dans le quadrilatère, sur un calque transparent
    de la taille du canevas."""
    src = [(0, 0), (image.width, 0), (image.width, image.height), (0, image.height)]
    c = homographie(quad, src)
    rgba = image.convert("RGBA")
    return rgba.transform(taille_canevas, Image.PERSPECTIVE, c,
                          resample=Image.BICUBIC)


# calques d'instructions / promotion livrés avec les gabarits : à ignorer
PARASITES = ("delete this", "how to use", "edit content", "place your design",
             "read me", "instructions", "pixelbuddha", "licence", "license",
             "change this", "double click", "ai photo base")


def parasite(nom):
    n = nom.lower()
    return any(m in n for m in PARASITES)


def au_dessus(psd, cible):
    """Les calques visibles au-dessus de l'emplacement, à recomposer —
    hors calques d'instructions livrés avec le gabarit."""
    plat = list(tous_les_calques(psd))
    i = plat.index(cible)
    gardes = []
    for l in plat[i + 1:]:
        if not l.visible or l.is_group() or not l.width or not l.height:
            continue
        if parasite(l.name):
            print(f"  (ignoré : « {l.name[:46]} »)")
            continue
        gardes.append(l)
    return gardes


def composer(chemin_psd, nom_calque, image, remplir=True):
    psd = PSDImage.open(chemin_psd)
    cible = next((l for l in tous_les_calques(psd)
                  if type(l).__name__ == "SmartObjectLayer"
                  and nom_calque.lower() in l.name.lower()), None)
    if cible is None:
        raise SystemExit(f"aucun objet dynamique nommé « {nom_calque} »")

    q = coins(cible)
    scene = psd.composite().convert("RGB")
    droit = est_droit(q)

    # dimensions utiles du placement (côtés du quadrilatère)
    import math
    lw = round(math.dist(q[0], q[1]))
    lh = round(math.dist(q[1], q[2]))
    print(f"  emplacement : {lw}×{lh} px  —  ratio {lw/lh:.3f}  "
          f"({'droit' if droit else 'incliné, projection en perspective'})")
    print(f"  image       : {image.width}×{image.height}  —  ratio {image.width/image.height:.3f}")

    # on remplit en recadrant au centre (le ratio du gabarit diffère souvent)
    if remplir:
        r = max(lw / image.width, lh / image.height)
        im = image.resize((max(1, round(image.width * r)), max(1, round(image.height * r))),
                          Image.LANCZOS)
        gx, gy = (im.width - lw) // 2, (im.height - lh) // 2
        im = im.crop((gx, gy, gx + lw, gy + lh))
    else:
        im = image.resize((lw, lh), Image.LANCZOS)

    if droit:
        scene.paste(im, (round(min(p[0] for p in q)), round(min(p[1] for p in q))))
    else:
        calque = projeter(im, q, scene.size)
        scene.paste(calque, (0, 0), calque)

    # on repose les ombres, cadres et reflets qui étaient au-dessus
    n = 0
    for l in au_dessus(psd, cible):
        try:
            vignette = l.composite()
        except Exception:
            continue
        if vignette is None:
            continue
        scene.paste(vignette.convert("RGBA"), (l.left, l.top), vignette.convert("RGBA"))
        n += 1
    print(f"  {n} calque(s) recomposé(s) par-dessus")
    return scene


def enregistrer(im, n, carre=True):
    if carre:
        c = min(im.size)
        im = im.crop(((im.width - c) // 2, (im.height - c) // 2,
                      (im.width + c) // 2, (im.height + c) // 2))
    for suf, large, q in (("", 1000, 80), ("@full", 1800, 82)):
        v = im.copy()
        r = large / max(v.size)
        if r < 1:
            v = v.resize((round(v.width * r), round(v.height * r)), Image.LANCZOS)
        v.convert("RGB").save(IMG / f"{n}{suf}.webp", "WEBP", quality=q, method=6)
    a = (IMG / f"{n}.webp").stat().st_size // 1024
    b = (IMG / f"{n}@full.webp").stat().st_size // 1024
    print(f"  → assets/img/{n}.webp  {a} Ko   ·   {n}@full.webp  {b} Ko")


def poser_telephone(scene, spec_ecran, part=0.58, carre=True):
    """Ajoute un iPhone au premier plan, à droite — en le gardant à
    l'intérieur du recadrage carré final, sinon il serait tronqué."""
    import mockup

    tel = mockup.telephone(ouvrir(spec_ecran), round(scene.height * part))

    if carre:                       # bord droit du futur carré centré
        cote = min(scene.size)
        droite = (scene.width + cote) // 2
    else:
        droite = scene.width
    marge = round(cote * 0.04) if carre else round(scene.width * 0.04)
    x = droite - tel.width - marge
    y = scene.height - tel.height - round(scene.height * 0.07)

    # ombre portée au sol, bien diffuse
    couche = Image.new("L", scene.size, 0)
    ImageDraw.Draw(couche).rounded_rectangle(
        (x + 26, y + 40, x + tel.width + 10, y + tel.height + 30),
        round(tel.width * .14), fill=120)
    scene.paste(Image.new("RGB", scene.size, (28, 26, 24)), (0, 0),
                couche.filter(ImageFilter.GaussianBlur(60)))
    scene.paste(tel, (x, y), tel)
    print(f"  téléphone posé : {tel.width}×{tel.height} px en ({x}, {y})")
    return scene


def opt(nom, defaut=None):
    return sys.argv[sys.argv.index(nom) + 1] if nom in sys.argv else defaut


if __name__ == "__main__":
    chemin = opt("--psd")
    if not chemin:
        raise SystemExit("il faut --psd <fichier.psd>")
    if "--lister" in sys.argv:
        lister(PSDImage.open(chemin))
        raise SystemExit(0)
    scene = composer(chemin, opt("--calque", "design"), ouvrir(opt("--src", "57")),
                     remplir="--entier" not in sys.argv)
    if opt("--telephone"):
        scene = poser_telephone(scene, opt("--telephone"), carre="--plein" not in sys.argv)
    enregistrer(scene, int(opt("--n", "99")), carre="--plein" not in sys.argv)
