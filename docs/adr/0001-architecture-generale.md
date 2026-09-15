# ADR-0001 — Architecture générale

- **Statut** : Accepté
- **Date** : 2026-09-15

## Contexte

Hestia est un boîtier **plug & play** de protection de la vie privée pour un
foyer. Il tourne sur une Raspberry Pi, affiche des informations sur un écran
e-paper, et doit héberger le **DHCP et le DNS** du réseau du foyer (blocage des
pubs et traqueurs, DNS chiffré vers l'extérieur). Les boîtiers sont installés
chez des particuliers et se mettent à jour automatiquement.

La question centrale : faut-il tout développer, ou s'appuyer sur des briques
existantes ?

## Décision

On sépare le système en deux couches :

1. **Le moteur réseau** = un composant existant et éprouvé (voir ADR-0003 :
   AdGuard Home) qui assure DHCP, DNS, filtrage et DNS chiffré. On ne réinvente
   pas le DNS.
2. **L'agent Hestia** = notre logiciel (voir ADR-0004 : Python), une *surcouche*
   qui :
   - configure le moteur et gère le premier démarrage,
   - lit les statistiques via l'API du moteur,
   - pilote l'écran e-paper,
   - gère les mises à jour (voir ADR-0005).

Le boîtier **remplace le serveur DHCP de la box** du foyer (l'utilisateur
désactive celui de sa box).

## Conséquences

- ✅ On se concentre sur l'expérience produit (écran, plug & play, flotte), pas
  sur la réimplémentation d'un serveur DNS.
- ✅ Fiabilité : le cœur réseau est un logiciel mature.
- ⚠️ On dépend d'AdGuard Home et de la stabilité de son API.
- ⚠️ Le boîtier devient un élément **central et critique** du réseau du foyer :
  s'il tombe, plus de résolution DNS. Prévoir robustesse et supervision.
- ⚠️ « Remplacer le DHCP de la box » impose une étape de configuration initiale
  côté utilisateur : ce n'est pas 100 % automatique (voir le défi d'onboarding).
