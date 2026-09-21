# Hestia en conteneurs (Docker / Podman)

Montage **appliance headless / e-paper** : deux conteneurs en **réseau host**,
AdGuard Home (moteur DNS/DHCP) et l'agent Hestia. Alternative au déploiement
systemd (`docs/INSTALL.md`), pas un ajout.

## Pourquoi réseau host + privilèges

Hestia sert le DHCP/DNS du foyer et sonde le réseau. Le conteneur a donc besoin :

- **`network_mode: host`** : servir le port 53, et voir les broadcasts DHCP du LAN ;
- **`CAP_NET_RAW`** (agent) : sonde DHCP scapy (sockets bruts) ;
- **`CAP_NET_ADMIN`** (AdGuard) : serveur DHCP d'AdGuard Home ;
- **devices `/dev/spidev*`, `/dev/gpiomem`** : écran e-paper.

→ En **Podman**, il faut du **rootful** (le rootless ne fait pas le host DHCP).

## Prérequis sur l'hôte (Raspberry Pi)

1. Docker (`curl -fsSL https://get.docker.com | sh`) ou Podman + `podman-compose`.
2. **Libérer le port 53** (systemd-resolved) — voir l'étape 2 de `docs/INSTALL.md`.
3. **SPI activé** si écran e-paper : `sudo raspi-config nonint do_spi 0`.
4. Créer la configuration et l'état sur l'hôte :
   ```bash
   sudo mkdir -p /etc/hestia /var/lib/hestia
   sudo cp config.example.toml /etc/hestia/config.toml   # puis éditer
   ```
   Avec le réseau host, gardez `base_url = "http://127.0.0.1:3000"`. Sur une Pi
   **sans écran e-paper**, mettez `display.kind = "console"` (les journaux du
   conteneur tiennent lieu de sortie).

## Lancer

```bash
docker compose up -d --build      # ou : podman-compose up -d
```

Puis configurez AdGuard Home sur `http://<ip-de-la-pi>:3000` (identifiant, mot de
passe, DNS chiffré en amont) et reportez l'identifiant/mot de passe dans
`/etc/hestia/config.toml`, puis `docker compose restart hestia-agent`.

Journaux et état :
```bash
docker compose logs -f hestia-agent
docker compose ps
```

## Écran e-paper

Le pilote Waveshare est intégré à l'image (build arg `WAVESHARE=1`, par défaut).
Adaptez les `devices` de `compose.yaml` à votre matériel, et `display.model` à
votre écran. Pour une image **sans** écran (dev/headless), construisez avec
`--build-arg WAVESHARE=0` et retirez la section `devices`.

> La **fenêtre bureau** n'est pas prévue en conteneur (pas de session graphique) :
> ce montage vise l'e-paper ou la sortie journaux.

## Démarrage au boot

- **Docker** : `restart: unless-stopped` (déjà dans le compose) relance au boot si
  le service Docker démarre au boot (`sudo systemctl enable docker`).
- **Podman** : générer des unités systemd (Quadlet, ou `podman generate systemd`)
  pour un démarrage géré par l'hôte.

## Mises à jour (important)

En conteneur, on met à jour en **tirant une nouvelle image**, pas via le mécanisme
OTA interne (archives signées) :

```bash
docker compose pull && docker compose up -d      # images publiées
# ou, en build local :
git -C /opt/hestia pull && docker compose up -d --build
```

Le service `hestia-updater` et son timer (déploiement systemd) **ne s'appliquent
pas** ici. Autrement dit, le conteneur **remplace** la chaîne OTA par le cycle
d'images. À trancher selon votre stratégie de flotte.

## Dépannage

- **Port 53 occupé** → systemd-resolved encore actif (voir prérequis).
- **Sonde DHCP qui échoue** → `CAP_NET_RAW` et `network_mode: host` présents ?
- **Écran vide** → devices SPI/GPIO passés ? `display.model` correct ? SPI activé ?
- **AdGuard injoignable depuis l'agent** → identifiant/mot de passe dans
  `config.toml`, et AdGuard bien configuré sur `:3000`.
