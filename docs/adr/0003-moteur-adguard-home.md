# ADR-0003 — Moteur réseau : AdGuard Home

- **Statut** : Accepté
- **Date** : 2026-09-15

## Contexte

Le boîtier doit fournir DHCP, DNS, filtrage pub/traqueurs et **DNS chiffré vers
l'extérieur (DoH/DoT)**. Trois options : construire sur mesure
(Unbound/CoreDNS + notre code), Pi-hole, ou AdGuard Home.

## Décision

On retient **AdGuard Home** comme moteur, et Hestia en fait une **surcouche**.

AdGuard Home fournit en un seul binaire : serveur DHCP, serveur DNS, filtrage par
listes, **upstreams DNS chiffrés (DoH/DoT)**, interface web **et une API REST**.

- Le **DNS chiffré** est une simple **configuration d'upstreams** (ex. Quad9,
  Cloudflare) : aucune ligne de code à écrire pour cette exigence.
- L'agent Hestia pilote AdGuard Home via son **API REST** (lecture des
  statistiques, réglages) plutôt qu'en réimplémentant ces fonctions.

Pi-hole a été écarté : DNS chiffré moins intégré, et architecture
(dnsmasq + FTL + PHP) moins simple à piloter par API qu'AdGuard Home.

## Conséquences

- ✅ Gain de temps considérable : le cœur réseau est fourni et éprouvé.
- ✅ Exigence « DNS chiffré » couverte par la configuration.
- ⚠️ L'**interface d'administration** d'AdGuard Home doit être protégée (mot de
  passe fort, non exposée hors du réseau local).
- ⚠️ On suit le rythme de versions d'AdGuard Home ; figer une version testée dans
  l'image et la mettre à jour de façon maîtrisée.
- ⚠️ Respect de la licence d'AdGuard Home à vérifier pour la distribution.
