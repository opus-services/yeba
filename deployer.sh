#!/bin/bash
# Installation et mise à jour du site sur le serveur Opalstack, à lancer en SSH depuis ce dossier :
#   bash deployer.sh            installe les dépendances, met à jour la base, prépare les fichiers statiques, redémarre
#   bash deployer.sh --premier  pareil, et crée les pages de départ (première installation)
# Prérequis : .env rempli (copie de .env.exemple). Voir MISE-EN-LIGNE.md.
set -euo pipefail
cd "$(dirname "$0")"
APP_DIR="$(cd .. && pwd)"                      # dossier de l'application Opalstack (~/apps/yeba)
PYTHON="${PYTHON:-$APP_DIR/env/bin/python}"    # environnement Python créé par Opalstack
[ -x "$PYTHON" ] || PYTHON="$(command -v python3)"

[ -f .env ] || { echo "Fichier .env absent : copier .env.exemple en .env et le remplir."; exit 1; }
mkdir -p logs sauvegardes

echo "1/6 Sauvegarde de la base avant mise à jour"
if [ -f db.sqlite3 ]; then cp db.sqlite3 "sauvegardes/db_$(date +%Y-%m-%d_%H%M).sqlite3"; fi
{ ls -1t sauvegardes/db_*.sqlite3 2>/dev/null || true; } | tail -n +15 | xargs -r rm -f   # on garde les 14 dernières

echo "2/6 Dépendances Python"
"$PYTHON" -m pip install --quiet --upgrade pip
"$PYTHON" -m pip install --quiet -r requirements.txt

echo "3/6 Vérification des réglages de production"
"$PYTHON" manage.py check --deploy --fail-level WARNING

echo "4/6 Fichiers statiques"
"$PYTHON" manage.py collectstatic --noinput --clear -v0

echo "5/6 Base de données"
"$PYTHON" manage.py migrate --noinput
if [ "${1:-}" = "--premier" ]; then
  "$PYTHON" manage.py peupler_yeba
fi
"$PYTHON" manage.py shell --no-imports -c "from django.core.cache import cache; cache.clear()" || true

echo "6/6 Redémarrage"
if [ -x "$APP_DIR/stop" ] && [ -x "$APP_DIR/start" ]; then
  "$APP_DIR/stop" || true
  "$APP_DIR/start"
else
  touch config/wsgi.py   # uWSGI recharge l'application si touch-reload pointe sur ce fichier
fi
echo "Terminé."
