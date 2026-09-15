# ADR-0004 — Langage de l'agent : Python

- **Statut** : Accepté
- **Date** : 2026-09-15

## Contexte

L'agent Hestia (voir ADR-0001) orchestre AdGuard Home, pilote l'écran e-paper et
gère les mises à jour. L'équipe n'a pas de langage dominant imposé. Le composant
réseau critique en performance (AdGuard Home) est déjà écrit en Go : l'agent, lui,
n'est pas critique en performance.

## Décision

L'agent est écrit en **Python**.

Raisons :
- **Meilleur support des écrans e-paper** : les bibliothèques Waveshare
  officielles sont en Python, avec de nombreux exemples pour Raspberry Pi.
- **Rapidité de développement** : adapté à une équipe polyvalente qui doit
  avancer vite.
- Appeler l'**API REST** d'AdGuard Home est trivial (bibliothèque `requests` ou
  `httpx`).
- La performance n'est pas un enjeu ici : le travail lourd est fait par AdGuard
  Home.

## Conséquences

- ✅ Prototypage rapide, écosystème riche pour la Pi.
- ⚠️ **Déploiement à soigner** : figer la version de Python, utiliser un
  environnement virtuel et un service `systemd`, épingler les dépendances
  (`requirements.txt`). Moins simple qu'un binaire unique (Go), mais acceptable
  vu le rôle non critique de l'agent.
- ⚠️ Fixer une version de Python cible (ex. celle de Raspberry Pi OS stable) pour
  toute la flotte, afin d'éviter les écarts entre appareils.
- 💡 Si le déploiement Python devenait un point de douleur, réévaluer Go pour
  l'agent (nouvel ADR).
