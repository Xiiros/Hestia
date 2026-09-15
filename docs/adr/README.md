# Décisions d'architecture (ADR)

Ce dossier trace les **décisions d'architecture** du projet Hestia, sous forme
d'*Architecture Decision Records* (ADR). Chaque fichier décrit **une** décision :
son contexte, le choix retenu et ses conséquences.

## Pourquoi

À plusieurs, on oublie vite *pourquoi* on a choisi telle techno. Un ADR répond à
« pourquoi AdGuard Home et pas Pi-hole ? » six mois plus tard, sans avoir à
retrouver la personne qui était là ce jour-là.

## Comment ça marche

- Un ADR est **court** (une page) et porte **une seule** décision.
- Une fois accepté, un ADR ne se réécrit pas : s'il devient obsolète, on en crée
  un nouveau qui le remplace (statut « Remplacé par ADR-XXXX »).
- Numérotation continue : `0001`, `0002`, …

## Index

| N° | Décision | Statut |
|----|----------|--------|
| [0001](0001-architecture-generale.md) | Architecture générale (moteur + agent) | Accepté |
| [0002](0002-materiel-raspberry-pi.md) | Matériel : Raspberry Pi + écran, pas d'ESP32 | Accepté |
| [0003](0003-moteur-adguard-home.md) | Moteur réseau : AdGuard Home | Accepté |
| [0004](0004-agent-python.md) | Langage de l'agent : Python | Accepté |
| [0005](0005-mises-a-jour-ota-maison.md) | Mises à jour : OTA « maison » | Accepté |
