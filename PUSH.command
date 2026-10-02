#!/bin/bash
# Double-clique ce fichier dans Finder pour pousser le site sur GitHub.
# Cloudflare Pages rebuild auto → lilanarinx.com mis à jour ~1-2 min.

cd "$(dirname "$0")" || exit 1

clear
echo "═══════════════════════════════════════════"
echo "  📤  PUSH PORTFOLIO → lilanarinx.com"
echo "═══════════════════════════════════════════"
echo ""

if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "✅ Aucun changement — rien à push."
  echo ""
  echo "(Cette fenêtre se ferme dans 3s)"
  sleep 3
  exit 0
fi

echo "📝 Changements détectés :"
git status --short
echo ""

git add -A
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
git commit -m "update ($TIMESTAMP)" || { echo "❌ Commit échoué"; sleep 5; exit 1; }

echo ""
echo "🚀 Push vers GitHub..."
if git push origin main; then
  echo ""
  echo "═══════════════════════════════════════════"
  echo "  ✅  PUSH RÉUSSI"
  echo "  🌍  https://lilanarinx.com"
  echo "  ⏱   Rebuild Cloudflare ~1-2 min"
  echo "═══════════════════════════════════════════"
else
  echo ""
  echo "❌ Push échoué — vérifie ta connexion / credentials git."
fi

echo ""
echo "(Tu peux fermer cette fenêtre)"
