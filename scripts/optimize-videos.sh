#!/bin/bash
# Compresse les vidéos de media/videos/ vers assets/video/ (H.264 + AAC, faststart)
# et génère une image poster WebP pour chacune.
# Les .mp4 produits sont ceux à uploader sur Cloudflare R2.
cd "$(dirname "$0")/.." || exit 1
mkdir -p assets/video assets/img/posters

enc() { # $1=source  $2=nom de sortie  $3=hauteur max  $4=seconde du poster
  src="$1"; out="assets/video/$2.mp4"; poster="assets/img/posters/$2.webp"
  [ -f "$out" ] && { echo "✓ $2 (déjà fait)"; return; }
  echo "⚙️  $2 …"
  ffmpeg -nostdin -v error -y -i "$src" \
    -vf "scale=-2:'min($3,ih)':flags=lanczos" \
    -c:v libx264 -crf 23 -preset medium -pix_fmt yuv420p \
    -c:a aac -b:a 128k -movflags +faststart "$out" || { echo "❌ $2"; return; }
  ffmpeg -nostdin -v error -y -ss "$4" -i "$out" -frames:v 1 \
    -vf "scale=-2:'min(900,ih)'" -q:v 80 "$poster"
  s=$(du -m "$src" | cut -f1); o=$(du -m "$out" | cut -f1)
  echo "   $2 : ${s} Mo → ${o} Mo"
}

enc media/videos/tribe-agency/reel-akai-sushi.mp4                  reel-akai-sushi                  1920 2
enc media/videos/tribe-agency/reel-cuisine-gazzosa.mp4             reel-cuisine-gazzosa             1920 2
enc media/videos/tribe-agency/reel-cocktail-le-corbier.mov         reel-cocktail-le-corbier         1920 2
enc media/videos/tribe-agency/reel-cocktail-framboise-delhaize.mov reel-cocktail-framboise-delhaize 1920 2
enc media/videos/tribe-agency/reel-post-it-ono.mov                 reel-post-it-ono                 1920 1
enc media/videos/tribe-agency/reel-cuisine-ono.mov                 reel-cuisine-ono                 1920 2
enc media/videos/vendredi-apero/apero-final.mp4                    apero-final                      1920 3
enc media/videos/vendredi-apero/poker-final.mp4                    poker-final                      1920 3
enc media/videos/reportage-spear/projet-spear.mov                  projet-spear                     1080 8
enc media/videos/erasmus-pub/pub-erasmus-1.mp4                     pub-erasmus-1                     720 3
enc media/videos/erasmus-pub/pub-erasmus-2.mp4                     pub-erasmus-2                     720 3

echo; echo "=== TOTAL ==="; du -sh assets/video
