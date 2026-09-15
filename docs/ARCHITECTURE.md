# Architecture de Hestia

Ce document donne la vue d'ensemble technique. Les décisions et leur *pourquoi*
sont dans [`docs/adr/`](adr/).

## Vue d'ensemble

Hestia est un boîtier plug & play de protection de la vie privée pour un foyer,
sur Raspberry Pi. Il se compose de deux couches :

- **Le moteur** : [AdGuard Home](https://adguard.com/fr/adguard-home/overview.html)
  assure DHCP, DNS, filtrage pub/traqueurs et DNS chiffré (DoH/DoT).
- **L'agent Hestia** (notre code, en Python) : orchestre le moteur, pilote
  l'écran e-paper et gère les mises à jour.

```
   Box Internet (DHCP désactivé)
        │ Ethernet
   ┌────▼─────────────────────────────────────────┐
   │  Raspberry Pi 4 — Raspberry Pi OS Lite 64-bit │
   │                                               │
   │  ┌─────────────────────────────────────────┐  │
   │  │ AdGuard Home  (DHCP · DNS · filtrage ·   │  │
   │  │               DoH/DoT)                   │  │
   │  └──────────────▲──────────────────────────┘  │
   │                 │ API REST (localhost)         │
   │  ┌──────────────┴──────────────────────────┐  │
   │  │ Agent Hestia (Python, service systemd)   │  │
   │  │  config · stats · écran · updater        │  │
   │  └──────────────┬──────────────────────────┘  │
   │                 │ SPI (GPIO)                    │
   │          ┌──────▼──────┐                        │
   │          │ Écran e-paper│                       │
   │          └─────────────┘                        │
   └────────────────────────────────────────────────┘
```

## Flux principaux

- **Affichage** : l'agent interroge l'API d'AdGuard Home à intervalle régulier
  (requêtes totales/bloquées, statut) et met à jour l'écran e-paper en
  **rafraîchissement partiel** (l'e-paper est lent : viser un affichage
  semi-statique, pas une animation).
- **Mises à jour** : l'updater vérifie le canal (beta/stable) sur les releases
  GitHub, télécharge la version, **vérifie sa signature**, l'applique, lance un
  **contrôle de santé**, et **revient en arrière** en cas d'échec. Détails dans
  [docs/OTA.md](OTA.md) (voir aussi [ADR-0005](adr/0005-mises-a-jour-ota-maison.md)).
- **Premier démarrage** : l'agent guide la configuration (l'utilisateur doit
  désactiver le DHCP de sa box), idéalement via une page de config locale, et
  **détecte un éventuel DHCP concurrent** sur le réseau pour éviter les conflits.

## Structure du dépôt (couche agent)

Le projet Python est géré par [uv](https://docs.astral.sh/uv/) (structure `src/`).

```
src/hestia/                # paquet Python de l'agent
├── app.py                 # point d'entrée / boucle principale
├── settings.py            # configuration (TOML + valeurs par défaut)
├── adguard/               # client de l'API AdGuard Home (stats, statut)
├── display/               # interface d'affichage : console (dev) + e-paper
├── onboarding/            # 1er démarrage : détection DHCP + tutoriels par box
├── system/               # réseau : sonde DHCP, identification de la box
└── updater/               # OTA : source GitHub, signature, install atomique + rollback

tests/                     # tests unitaires (pytest)
systemd/                   # unités systemd (hestia-agent…)
pyproject.toml             # métadonnées, dépendances, outillage
uv.lock                    # dépendances verrouillées
```

Dépendances optionnelles (extras) : `net` (scapy, sonde DHCP) et `hardware`
(Pillow, rendu e-paper) — non requises pour les tests. Commandes utiles :

```bash
uv sync --group dev        # environnement de développement
uv run hestia --demo       # démonstration sans matériel ni AdGuard Home
uv run ruff check . && uv run pytest
```

Le fichier [`VERSION`](../VERSION) (déjà présent) est la version affichée à
l'écran et la référence de l'updater pour comparer les versions.

## Points de vigilance (logiciel de vie privée)

- Le boîtier voit **toutes** les requêtes DNS du foyer : **aucune télémétrie** ne
  doit sortir du foyer sans consentement explicite.
- Interface d'administration d'AdGuard Home protégée et non exposée hors du LAN.
- Mises à jour **signées** et vérifiées côté appareil.

## Matériel

Voir [ADR-0002](adr/0002-materiel-raspberry-pi.md) : Raspberry Pi 4 (2 Go),
Ethernet filaire obligatoire, écran e-paper Waveshare 2.9"/4.2" en SPI.
