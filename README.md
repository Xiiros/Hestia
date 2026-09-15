# Hestia

Boîtier **plug & play** de protection de la vie privée pour un foyer. Sur une
Raspberry Pi équipée d'un écran e-paper, Hestia héberge le DHCP et le DNS du
réseau domestique pour **bloquer pubs et traqueurs** et **chiffrer les requêtes
DNS** vers l'extérieur.

## Comment ça marche

Hestia s'appuie sur [AdGuard Home](https://adguard.com/fr/adguard-home/overview.html)
comme moteur réseau (DHCP, DNS, filtrage, DoH/DoT) et y ajoute une surcouche
maison : orchestration, tableau de bord sur écran e-paper, et mises à jour à
distance.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — vue d'ensemble technique.
- [Mises à jour OTA](docs/OTA.md) — signature, canaux, installation avec rollback.
- [Décisions d'architecture (ADR)](docs/adr/) — les choix techniques et leur *pourquoi*.
- [Contribuer](CONTRIBUTING.md) — branches, commits, revues et fusions.
- [Sortir une version](docs/RELEASING.md) — releases et déploiement sur la flotte.

## État du projet

En conception. La structure de la couche agent (Python) est esquissée dans le
document d'architecture.
