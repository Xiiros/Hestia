#!/usr/bin/env bash
# Génère la paire de clés Ed25519 pour signer les mises à jour OTA.
#
#   - update-key.pem : clé PRIVÉE. À stocker dans le secret GitHub
#     UPDATE_SIGNING_KEY. Ne JAMAIS la committer ni la mettre sur un boîtier.
#   - update-key.pub : clé PUBLIQUE. À déployer sur chaque Raspberry Pi
#     (chemin update.public_key_path, par défaut /etc/hestia/update-key.pub).
set -euo pipefail

openssl genpkey -algorithm ed25519 -out update-key.pem
openssl pkey -in update-key.pem -pubout -out update-key.pub

echo "Clé privée : update-key.pem  -> secret GitHub UPDATE_SIGNING_KEY"
echo "Clé publique : update-key.pub -> /etc/hestia/update-key.pub sur les Pi"
