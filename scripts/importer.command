#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  IMPORTER — double-clique ce fichier.
#  Tout ce qui se trouve dans « _DEPOSER-ICI » est préparé pour le site :
#    · les images  → redimensionnées en WebP dans assets/img/
#    · les vidéos  → compressées en MP4 dans assets/video/ + une image fixe
#  Les originaux sont rangés dans media/, rien n'est supprimé.
# ═══════════════════════════════════════════════════════════════════
cd "$(dirname "$0")/.." || exit 1
DEPOT="_DEPOSER-ICI"
mkdir -p "$DEPOT" assets/img assets/img/posters assets/video media/photos/importe media/videos/importe

clear
echo "═══════════════════════════════════════════"
echo "  📥  IMPORTER LES NOUVEAUX CONTENUS"
echo "═══════════════════════════════════════════"
echo ""

NB=$(find "$DEPOT" -type f ! -name ".*" | wc -l | tr -d ' ')
if [ "$NB" -eq 0 ]; then
  echo "Le dossier « $DEPOT » est vide."
  echo ""
  echo "Glisse dedans tes photos (.jpg .png .heic) et tes vidéos"
  echo "(.mp4 .mov), puis double-clique à nouveau ce fichier."
  echo ""
  read -n 1 -s -r -p "(appuie sur une touche pour fermer)"
  exit 0
fi

echo "$NB fichier(s) à traiter."
echo ""

python3 scripts/importer.py || { echo; echo "❌ L'import a échoué."; read -n 1 -s -r -p "(touche pour fermer)"; exit 1; }

echo ""
echo "🔨 Régénération du site…"
python3 scripts/build.py | tail -1

echo ""
echo "═══════════════════════════════════════════"
echo "  ✅  TERMINÉ"
echo "═══════════════════════════════════════════"
echo ""
echo "Prochaines étapes :"
echo "  1. Ouvre scripts/content.py et ajoute les numéros indiqués"
echo "     ci-dessus dans la bonne rubrique."
echo "  2. Relance scripts/build.py (ou re-double-clique ce fichier)."
echo "  3. Double-clique scripts/PUSH.command pour mettre en ligne."
echo ""
echo "  Les vidéos sont dans assets/video/ : à déposer sur Cloudflare R2"
echo "  (voir docs/DEPLOY.md)."
echo ""
read -n 1 -s -r -p "(appuie sur une touche pour fermer)"
