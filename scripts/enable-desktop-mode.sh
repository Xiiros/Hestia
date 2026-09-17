#!/usr/bin/env bash
# Bascule Hestia en « mode bureau » : l'agent démarre dans la session graphique
# de l'utilisateur (pour afficher la fenêtre quand il n'y a pas d'écran e-paper),
# et non plus via le service systemd root.
#
# - accorde CAP_NET_RAW à l'interpréteur Python du venv, pour que la sonde DHCP
#   (scapy) fonctionne SANS root ;
# - installe l'entrée d'autostart dans la session de l'utilisateur ;
# - désactive le service root hestia-agent (évite deux agents en parallèle).
#
# À lancer en root :  sudo ./scripts/enable-desktop-mode.sh
#
# Variables :
#   HESTIA_DIR    (défaut : /opt/hestia)
#   HESTIA_USER   utilisateur du bureau (défaut : $SUDO_USER, sinon "pi")
set -euo pipefail

HESTIA_DIR="${HESTIA_DIR:-/opt/hestia}"
HESTIA_USER="${HESTIA_USER:-${SUDO_USER:-pi}}"

log() { printf '\n\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }

if [ "$(id -u)" -ne 0 ]; then
  echo "Ce script doit être lancé en root : sudo $0" >&2
  exit 1
fi

if ! command -v setcap >/dev/null 2>&1; then
  log "Installation de libcap2-bin (setcap)"
  apt-get install -y -qq libcap2-bin
fi

# 1. Capacité réseau pour la sonde DHCP sans root.
venv_py="$HESTIA_DIR/.venv/bin/python"
[ -e "$venv_py" ] || { echo "Interpréteur introuvable : $venv_py (lancez install.sh d'abord)." >&2; exit 1; }
real_py="$(readlink -f "$venv_py")"
log "Attribution de CAP_NET_RAW à $real_py"
setcap cap_net_raw+eip "$real_py"
warn "Note sécurité : la capacité s'applique à cet interpréteur ; sur un boîtier"
warn "dédié à Hestia c'est acceptable, sinon isolez l'interpréteur du venv."

# 2. Autostart dans la session du bureau de l'utilisateur.
user_home="$(getent passwd "$HESTIA_USER" | cut -d: -f6)"
[ -n "$user_home" ] || { echo "Utilisateur inconnu : $HESTIA_USER" >&2; exit 1; }
autostart_dir="$user_home/.config/autostart"
log "Installation de l'autostart pour l'utilisateur $HESTIA_USER"
install -d -m 0755 "$autostart_dir"
install -m 0644 "$HESTIA_DIR/autostart/hestia.desktop" "$autostart_dir/hestia.desktop"
chown -R "$HESTIA_USER":"$HESTIA_USER" "$autostart_dir"

# 3. Désactiver le service root (l'agent tourne désormais via l'autostart).
log "Désactivation du service root hestia-agent"
systemctl disable --now hestia-agent.service >/dev/null 2>&1 || true

log "Mode bureau activé."
echo "L'agent démarrera dans la session de $HESTIA_USER à la prochaine ouverture"
echo "de session. Le timer de mises à jour (hestia-updater) reste actif."
