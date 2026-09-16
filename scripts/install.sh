#!/usr/bin/env bash
# Installe ou met à jour Hestia sur une Raspberry Pi (étapes 4 à 7 du guide
# docs/INSTALL.md). Idempotent : relançable sans risque.
#
# À lancer en root :  sudo ./scripts/install.sh
#
# Variables d'environnement (facultatives) :
#   REPO_URL           dépôt à cloner (défaut : https://github.com/Xiiros/Hestia.git)
#   REPO_REF           branche ou tag à déployer (défaut : main)
#   INSTALL_WAVESHARE  =1 pour installer le pilote e-paper Waveshare
#   START_AGENT        =1 pour démarrer l'agent tout de suite (défaut : non)
set -euo pipefail

HESTIA_DIR="/opt/hestia"
CONFIG_DIR="/etc/hestia"
STATE_DIR="/var/lib/hestia"
REPO_URL="${REPO_URL:-https://github.com/Xiiros/Hestia.git}"
REPO_REF="${REPO_REF:-main}"

log() { printf '\n\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }

if [ "$(id -u)" -ne 0 ]; then
  echo "Ce script doit être lancé en root : sudo $0" >&2
  exit 1
fi

# --- Dépendances système -----------------------------------------------------
log "Dépendances système"
if command -v apt-get >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y -qq git openssl python3 fonts-dejavu-core
else
  warn "apt-get introuvable : installez git, openssl et python3 manuellement."
fi

if command -v raspi-config >/dev/null 2>&1; then
  log "Activation du SPI (écran e-paper)"
  raspi-config nonint do_spi 0 || warn "Activation du SPI impossible automatiquement."
fi

# --- uv ----------------------------------------------------------------------
if ! command -v uv >/dev/null 2>&1; then
  log "Installation de uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
UV="$(command -v uv || echo "$HOME/.local/bin/uv")"
[ -x "$UV" ] || { echo "uv introuvable après installation." >&2; exit 1; }

# --- Déploiement du code -----------------------------------------------------
if [ -d "$HESTIA_DIR/.git" ]; then
  log "Mise à jour du dépôt ($REPO_REF) dans $HESTIA_DIR"
  git -C "$HESTIA_DIR" fetch --quiet origin "$REPO_REF"
  git -C "$HESTIA_DIR" checkout --quiet "$REPO_REF" 2>/dev/null \
    || git -C "$HESTIA_DIR" checkout --quiet -B "$REPO_REF" "origin/$REPO_REF"
  git -C "$HESTIA_DIR" merge --quiet --ff-only "origin/$REPO_REF" 2>/dev/null || true
else
  log "Clonage du dépôt ($REPO_REF) dans $HESTIA_DIR"
  git clone --branch "$REPO_REF" "$REPO_URL" "$HESTIA_DIR"
fi

# --- Environnement Python ----------------------------------------------------
log "Dépendances Python (uv sync)"
(cd "$HESTIA_DIR" && "$UV" sync --extra net --extra hardware --extra ota)

# --- Pilote e-paper Waveshare (optionnel) ------------------------------------
if [ "${INSTALL_WAVESHARE:-0}" = "1" ]; then
  log "Pilote e-paper Waveshare"
  tmp="$(mktemp -d)"
  git clone --depth 1 https://github.com/waveshare/e-Paper.git "$tmp"
  site="$(cd "$HESTIA_DIR" && "$UV" run python -c 'import site; print(site.getsitepackages()[0])')"
  cp -r "$tmp/RaspberryPi_JetsonNano/python/lib/waveshare_epd" "$site/"
  rm -rf "$tmp"
else
  warn "Pilote Waveshare non installé (relancez avec INSTALL_WAVESHARE=1)."
fi

# --- Configuration -----------------------------------------------------------
log "Répertoires de configuration et d'état"
mkdir -p "$CONFIG_DIR" "$STATE_DIR"
if [ ! -f "$CONFIG_DIR/config.toml" ]; then
  cp "$HESTIA_DIR/config.example.toml" "$CONFIG_DIR/config.toml"
  warn "Config créée : $CONFIG_DIR/config.toml — À ÉDITER (mot de passe AdGuard, écran, DHCP)."
else
  log "Config existante conservée : $CONFIG_DIR/config.toml"
fi

# --- Services systemd --------------------------------------------------------
log "Services systemd"
cp "$HESTIA_DIR"/systemd/hestia-agent.service \
   "$HESTIA_DIR"/systemd/hestia-updater.service \
   "$HESTIA_DIR"/systemd/hestia-updater.timer \
   /etc/systemd/system/
systemctl daemon-reload
systemctl enable hestia-agent.service >/dev/null
systemctl enable --now hestia-updater.timer >/dev/null

if [ "${START_AGENT:-0}" = "1" ]; then
  log "Démarrage de l'agent"
  systemctl restart hestia-agent.service
fi

# --- Récapitulatif -----------------------------------------------------------
log "Installation terminée."
cat <<EOF

Prochaines étapes :
  1. Installer et configurer AdGuard Home (http://<ip-de-la-pi>:3000) — étape 3 du guide.
  2. Éditer la configuration :   $CONFIG_DIR/config.toml
  3. Déposer la clé publique OTA : $CONFIG_DIR/update-key.pub
  4. Démarrer l'agent :          systemctl start hestia-agent.service
     Suivre les journaux :       journalctl -u hestia-agent.service -f

Guide complet : $HESTIA_DIR/docs/INSTALL.md
EOF
