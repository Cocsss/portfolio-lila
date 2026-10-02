#!/bin/bash
# Extrait une image poster WebP pour chaque vidéo de assets/video/.
# (l'encodeur webp de ffmpeg étant désactivé, on passe par cwebp)
cd "$(dirname "$0")/.." || exit 1
mkdir -p assets/img/posters
tmp=$(mktemp -d)
poser() { # $1=nom  $2=seconde
  v="assets/video/$1.mp4"; [ -f "$v" ] || { echo "⚠️  $1 absent"; return; }
  ffmpeg -nostdin -v error -y -ss "$2" -i "$v" -frames:v 1 \
         -vf "scale=-2:'min(900,ih)'" "$tmp/$1.png" || return
  cwebp -quiet -q 82 "$tmp/$1.png" -o "assets/img/posters/$1.webp"
  printf "  %-34s %s\n" "$1" "$(du -h "assets/img/posters/$1.webp" | cut -f1)"
}
poser reel-akai-sushi 2
poser reel-cuisine-gazzosa 2
poser reel-cocktail-le-corbier 2
poser reel-cocktail-framboise-delhaize 2
poser reel-post-it-ono 1
poser reel-cuisine-ono 2
poser apero-final 3
poser poker-final 3
poser projet-spear 35
poser pub-erasmus-1 3
poser pub-erasmus-2 3
rm -rf "$tmp"
