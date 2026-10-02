#!/usr/bin/env python3
"""Génère les versions web (WebP) des visuels depuis media/photos/ vers assets/img/.
   - <n>.webp      : version grille (long bord 1000 px)
   - <n>@full.webp : version lightbox (long bord 1800 px)
   Relancer après ajout/remplacement d'un visuel : python3 scripts/optimize-images.py
"""
import glob, os, sys
from PIL import Image, ImageOps

SRC, OUT = "media/photos", "assets/img"
GRID, FULL = 1000, 1800

def save(im, path, w, q):
    im = ImageOps.exif_transpose(im)
    r = min(1.0, w / max(im.size))
    if r < 1.0:
        im = im.resize((round(im.width*r), round(im.height*r)), Image.LANCZOS)
    if im.mode in ("RGBA", "P", "LA"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA"); bg.paste(im, mask=im.split()[-1]); im = bg
    else:
        im = im.convert("RGB")
    im.save(path, "WEBP", quality=q, method=6)
    return os.path.getsize(path)

os.makedirs(OUT, exist_ok=True)
files = sorted(
    (p for p in glob.glob(f"{SRC}/**/*.*", recursive=True)
     if p.lower().endswith((".png", ".jpg", ".jpeg"))),
    key=lambda p: int(os.path.basename(p).split(".")[0])
    if os.path.basename(p).split(".")[0].isdigit() else 999)

tot_src = tot_out = 0
for p in files:
    n = os.path.basename(p).split(".")[0]
    src = os.path.getsize(p); tot_src += src
    with Image.open(p) as im:
        w, h = im.size
        a = save(im.copy(), f"{OUT}/{n}.webp", GRID, 80)
        b = save(im.copy(), f"{OUT}/{n}@full.webp", FULL, 82)
    tot_out += a + b
    print(f"  {n:>3}  {w}x{h}  {src//1024:>6} Ko → {a//1024:>4} + {b//1024:>4} Ko")

print(f"\n{len(files)} visuels : {tot_src/1048576:.1f} Mo → {tot_out/1048576:.1f} Mo "
      f"({tot_out/tot_src*100:.0f} %)")
