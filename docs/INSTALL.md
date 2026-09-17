# Installer Hestia sur une Raspberry Pi

Ce guide décrit l'installation complète d'un boîtier Hestia sur une Raspberry Pi,
depuis une carte vierge jusqu'au service qui démarre tout seul.

> Les commandes sont à lancer sur la Raspberry Pi (en SSH ou clavier/écran), avec
> un utilisateur disposant de `sudo`.

> **Raccourci** : une fois les étapes 1 à 3 faites (système + AdGuard Home), le
> script [`scripts/install.sh`](../scripts/install.sh) automatise les étapes 4 à 7
> (déploiement, dépendances, config, services) :
>
> ```bash
> git clone https://github.com/Xiiros/Hestia.git /tmp/hestia && \
>   sudo INSTALL_WAVESHARE=1 /tmp/hestia/scripts/install.sh
> ```
>
> Les sections ci-dessous détaillent chaque étape (utile pour comprendre ou
> dépanner).

## 1. Prérequis

**Matériel**
- Raspberry Pi 4 (2 Go recommandé) — voir [ADR-0002](adr/0002-materiel-raspberry-pi.md).
- Carte microSD (16 Go ou plus) + alimentation officielle.
- **Câble Ethernet** : le boîtier sert le DHCP/DNS du foyer, il doit être filaire.
- Écran e-paper Waveshare (HAT SPI, ex. 2.13" `epd2in13_V4`).

**Système**
- Raspberry Pi OS **Lite 64-bit** (Bookworm), installé avec Raspberry Pi Imager.
  Pensez à activer SSH et à définir le nom d'utilisateur dans l'Imager.

## 2. Préparer le système

Mettre à jour et installer les outils de base :

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y git openssl python3 fonts-dejavu-core
```

**Activer le SPI** (nécessaire pour l'écran e-paper) :

```bash
sudo raspi-config nonint do_spi 0
```

**Libérer le port 53** — sur Raspberry Pi OS, `systemd-resolved` occupe le port 53
dont AdGuard Home a besoin. Désactiver son écoute DNS :

```bash
sudo mkdir -p /etc/systemd/resolved.conf.d
printf '[Resolve]\nDNSStubListener=no\n' | sudo tee /etc/systemd/resolved.conf.d/hestia.conf
sudo systemctl restart systemd-resolved
```

## 3. Installer AdGuard Home (le moteur DNS/DHCP)

Hestia est une surcouche : le moteur réseau est AdGuard Home
([ADR-0003](adr/0003-moteur-adguard-home.md)).

```bash
curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sh -s -- -v
```

Puis ouvrir `http://<ip-de-la-pi>:3000` dans un navigateur et suivre l'assistant :
- définir l'**identifiant et le mot de passe** d'administration (à reporter dans la
  config Hestia) ;
- laisser AdGuard Home gérer le DNS ;
- configurer un **DNS chiffré (DoH/DoT)** en amont (ex. Quad9, Cloudflare) dans
  *Paramètres → Paramètres DNS → Serveurs DNS en amont*.

Le service AdGuard s'appelle `AdGuardHome.service` (l'agent Hestia démarre après lui).

## 4. Installer Hestia

Installer **uv** (gestionnaire de paquets Python) :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Déployer le projet dans `/opt/hestia` (chemin attendu par les services) :

```bash
sudo mkdir -p /opt/hestia
sudo chown "$USER" /opt/hestia
git clone https://github.com/Xiiros/Hestia.git /opt/hestia
cd /opt/hestia
```

Créer l'environnement avec les extras matériels (`net` pour la sonde DHCP,
`hardware` pour l'écran, `ota` pour la vérification des mises à jour) :

```bash
uv sync --extra net --extra hardware --extra ota
```

Cela crée `/opt/hestia/.venv` avec les exécutables `hestia` et `hestia-update`.

Test rapide (rendu du tableau de bord dans un fichier PNG, sans matériel) :

```bash
uv run hestia --demo --png /tmp/apercu.png
```

## 5. Pilote de l'écran e-paper

Le pilote Waveshare (`waveshare_epd`) n'est pas sur PyPI ; il se récupère depuis le
dépôt Waveshare et se copie dans l'environnement :

```bash
git clone https://github.com/waveshare/e-Paper.git /tmp/e-Paper
cp -r /tmp/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd \
      /opt/hestia/.venv/lib/python3.*/site-packages/
```

> Le nom du module correspond au réglage `display.model` (par défaut `epd2in13_V4`).
> Adaptez-le au modèle réellement branché.

> **Repli fenêtre bureau** : si l'écran e-paper n'est pas détecté, l'agent peut
> afficher le flux dans une fenêtre sur le bureau. Cela requiert un environnement
> graphique et `python3-tk` : `sudo apt install -y python3-tk`.
>
> Tester la fenêtre (depuis un terminal **du bureau** de la Pi) :
>
> ```bash
> /opt/hestia/.venv/bin/hestia --demo --window
> ```
>
> ⚠️ **Au démarrage**, l'agent est lancé par un service systemd **root sans
> session graphique** (`$DISPLAY` absent) : la fenêtre ne peut donc pas s'ouvrir
> et l'agent retombe sur la console (voir `journalctl -u hestia-agent`). Pour
> afficher la fenêtre **automatiquement au boot**, activez le *mode bureau*
> ci-dessous.

### Mode bureau (fenêtre au démarrage, sans écran e-paper)

Ce mode fait démarrer l'agent **dans la session du bureau** (pour afficher la
fenêtre) au lieu du service root, et accorde à l'interpréteur Python la capacité
`CAP_NET_RAW` pour que la sonde DHCP fonctionne **sans root** :

```bash
sudo HESTIA_USER=pi /opt/hestia/scripts/enable-desktop-mode.sh
```

Ou directement à l'installation : `sudo INSTALL_AUTOSTART=1 .../scripts/install.sh`.

Le script installe l'autostart (`~/.config/autostart/hestia.desktop`), applique
`setcap` et désactive le service root `hestia-agent` (pour ne pas avoir deux
agents). Le timer de mises à jour reste actif.

> **Note sécurité** : `CAP_NET_RAW` est accordé à l'interpréteur du venv ; sur un
> boîtier dédié à Hestia c'est acceptable. Pour un usage e-paper classique (sans
> bureau), gardez le service root et ignorez ce mode.

## 6. Configuration

Créer les répertoires d'état et de configuration :

```bash
sudo mkdir -p /etc/hestia /var/lib/hestia
```

Copier l'exemple de configuration et l'adapter :

```bash
sudo cp /opt/hestia/config.example.toml /etc/hestia/config.toml
sudo nano /etc/hestia/config.toml
```

À renseigner en priorité :
- `[adguard]` : `password` (et `username`) définis à l'étape 3 ;
- `[display]` : `model`, `width`, `height` selon votre écran ;
- `[dhcp]` : pour que Hestia active le DHCP d'AdGuard à la fin du premier
  démarrage, mettre `enable_on_first_boot = true` **et** renseigner `gateway_ip`
  (l'IP de la box), `range_start`, `range_end`. Laissé à `false`, rien n'est
  activé automatiquement.

**Clé publique des mises à jour** — copier la clé publique OTA générée par l'équipe
(voir [docs/OTA.md](OTA.md)) :

```bash
sudo cp update-key.pub /etc/hestia/update-key.pub
```

## 7. Installer les services

```bash
sudo cp /opt/hestia/systemd/hestia-agent.service /etc/systemd/system/
sudo cp /opt/hestia/systemd/hestia-updater.service /etc/systemd/system/
sudo cp /opt/hestia/systemd/hestia-updater.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now hestia-agent.service      # l'agent (écran + orchestration)
sudo systemctl enable --now hestia-updater.timer      # mises à jour automatiques
```

> Les services tournent en root : la sonde DHCP (scapy) a besoin des privilèges
> réseau, et l'accès SPI à l'écran l'exige aussi.

## 8. Premier démarrage

Au tout premier lancement, Hestia sonde le réseau. Si le **DHCP de la box** est
encore actif, l'écran affiche le **tutoriel de désactivation** adapté à votre box.
Suivez-le (désactivez le serveur DHCP de la box), et dès que le conflit disparaît,
l'écran affiche « Hestia pret » : le boîtier prend le relais.

## 9. Vérifier et dépanner

```bash
systemctl status hestia-agent.service       # état de l'agent
journalctl -u hestia-agent.service -f        # journaux en direct
systemctl list-timers hestia-updater.timer   # prochaine vérification de MAJ
hestia-update() { /opt/hestia/.venv/bin/hestia-update; }   # forcer une vérif MAJ
```

Problèmes fréquents :
- **AdGuard indisponible** dans les journaux → vérifier `base_url`, l'identifiant
  et le mot de passe dans `config.toml`, et que `AdGuardHome.service` tourne.
- **Écran vide** → SPI activé (étape 2) ? Pilote `waveshare_epd` copié (étape 5) ?
  `display.model` correspond-il au modèle branché ?
- **Port 53 déjà utilisé** par AdGuard → revoir l'étape 2 (`DNSStubListener=no`).

## 10. Mises à jour

Aucune action manuelle : le *timer* `hestia-updater` vérifie chaque heure les
nouvelles versions signées et les applique (avec retour arrière automatique en cas
de problème). Détails dans [docs/OTA.md](OTA.md).
