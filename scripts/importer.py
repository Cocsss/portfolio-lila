#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prépare pour le site tout ce qui a été déposé dans « _DEPOSER-ICI ».

Lancé par scripts/importer.command (double-clic). Peut aussi se lancer seul :
    python3 scripts/importer.py

Images  → assets/img/<n>.webp (grille) + <n>@full.webp (visionneuse)
Vidéos  → assets/video/<nom>.mp4 + assets/img/posters/<nom>.webp
Les originaux sont déplacés dans media/, jamais supprimés.
"""
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
os.chdir(RACINE)

from PIL import Image, ImageOps

DEPOT   = Path("_DEPOSER-ICI")
IMG     = Path("assets/img")
POSTERS = IMG / "posters"
VIDEO   = Path("assets/video")
SRC_IMG = Path("media/photos/importe")
SRC_VID = Path("media/videos/importe")

IMAGES = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}
VIDEOS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}

GRILLE, PLEIN = 1000, 1800


def poids(o):
    return f"{o / 1048576:.1f} Mo" if o >= 1048576 else f"{o // 1024} Ko"


def propre(nom):
    """« Réel cuisine Ono.MOV » → « reel-cuisine-ono » (sûr pour une URL)."""
    base = unicodedata.normalize("NFKD", Path(nom).stem)
    base = base.encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return base or "sans-nom"


def prochain_numero():
    n = 0
    for f in IMG.glob("*.webp"):
        tige = f.stem.replace("@full", "")
        if tige.isdigit():
            n = max(n, int(tige))
    return n + 1


def enregistrer(im, chemin, large, qualite):
    im = ImageOps.exif_transpose(im)
    r = min(1.0, large / max(im.size))
    if r < 1.0:
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    if im.mode in ("RGBA", "P", "LA"):
        fond = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        fond.paste(im, mask=im.split()[-1])
        im = fond
    else:
        im = im.convert("RGB")
    im.save(chemin, "WEBP", quality=qualite, method=6)


def sans_ecraser(dossier, nom, suffixe):
    cible = dossier / f"{nom}{suffixe}"
    k = 2
    while cible.exists():
        cible = dossier / f"{nom}-{k}{suffixe}"
        k += 1
    return cible


def importer_image(f, numero):
    try:
        with Image.open(f) as im:
            w, h = im.size
            enregistrer(im.copy(), IMG / f"{numero}.webp", GRILLE, 80)
            enregistrer(im.copy(), IMG / f"{numero}@full.webp", PLEIN, 82)
    except Exception as exc:
        print(f"   ❌ {f.name} : {exc}")
        return None
    shutil.move(str(f), str(sans_ecraser(SRC_IMG, propre(f.name), f.suffix.lower())))
    ko = (IMG / f"{numero}.webp").stat().st_size // 1024
    print(f"   ✅ {f.name}  →  visuel {numero}   ({w}×{h}, {ko} Ko)")
    return numero


def importer_video(f):
    nom = propre(f.name)
    sortie = VIDEO / f"{nom}.mp4"
    k = 2
    while sortie.exists():
        sortie = VIDEO / f"{nom}-{k}.mp4"
        k += 1
    nom = sortie.stem

    print(f"   ⏳ {f.name} — compression…", flush=True)
    r = subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(f),
        "-vf", "scale=-2:'min(1280,ih)':flags=lanczos",
        "-c:v", "libx264", "-crf", "25", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(sortie),
    ])
    if r.returncode != 0 or not sortie.exists():
        print(f"   ❌ {f.name} : la compression a échoué")
        return None

    # image fixe : on prend une image à 2 s, convertie en WebP par Pillow
    tmp = POSTERS / f"{nom}.png"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", "2",
                    "-i", str(sortie), "-frames:v", "1",
                    "-vf", "scale=-2:'min(900,ih)'", str(tmp)])
    if tmp.exists():
        with Image.open(tmp) as im:
            im.convert("RGB").save(POSTERS / f"{nom}.webp", "WEBP", quality=82, method=6)
        tmp.unlink()

    avant = f.stat().st_size
    shutil.move(str(f), str(sans_ecraser(SRC_VID, nom, f.suffix.lower())))
    apres = sortie.stat().st_size
    print(f"   ✅ {f.name}  →  {sortie.name}   "
          f"({poids(avant)} → {poids(apres)})")
    return nom


def main():
    for d in (IMG, POSTERS, VIDEO, SRC_IMG, SRC_VID, DEPOT):
        d.mkdir(parents=True, exist_ok=True)

    fichiers = sorted(f for f in DEPOT.rglob("*")
                      if f.is_file() and not f.name.startswith("."))
    if not fichiers:
        print("Rien à importer.")
        return

    numero = prochain_numero()
    neufs_img, neufs_vid, ignores = [], [], []

    print("── Images ──")
    vus = False
    for f in fichiers:
        if f.suffix.lower() in IMAGES:
            vus = True
            if importer_image(f, numero):
                neufs_img.append(numero)
                numero += 1
    if not vus:
        print("   (aucune)")

    print("\n── Vidéos ──")
    vus = False
    for f in fichiers:
        if f.suffix.lower() in VIDEOS:
            vus = True
            n = importer_video(f)
            if n:
                neufs_vid.append(n)
    if not vus:
        print("   (aucune)")

    for f in fichiers:
        if (f.suffix.lower() not in IMAGES | VIDEOS
                and f.suffix.lower() not in {".txt", ".md"} and f.exists()):
            ignores.append(f.name)
    if ignores:
        print("\n── Ignorés (ni image ni vidéo) ──")
        for n in ignores:
            print(f"   ⚠️  {n}")

    print("\n" + "═" * 55)
    print("  À COLLER DANS scripts/content.py")
    print("═" * 55)
    if neufs_img:
        print(f'\n  "medias": img({", ".join(str(n) for n in neufs_img)}),')
    if neufs_vid:
        print(f'\n  "medias": vid({", ".join(chr(34) + n + chr(34) for n in neufs_vid)}),')
    if not neufs_img and not neufs_vid:
        print("\n  (rien de nouveau)")
    print()


if __name__ == "__main__":
    main()
