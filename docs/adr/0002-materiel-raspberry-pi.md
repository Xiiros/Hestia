# ADR-0002 — Matériel : Raspberry Pi + écran e-paper (pas d'ESP32)

- **Statut** : Accepté
- **Date** : 2026-09-15

## Contexte

Le boîtier doit faire tourner un moteur DNS/DHCP complet (AdGuard Home, un
binaire Go sous Linux, avec des listes de blocage de plusieurs centaines de
milliers de domaines), piloter un écran e-paper et gérer des mises à jour. La
question d'un ESP32 (moins cher) a été posée.

## Décision

- **Plateforme : Raspberry Pi.** Un ESP32 est **écarté** comme cerveau du
  boîtier : c'est un microcontrôleur (~520 Ko de RAM, pas de Linux), incapable de
  faire tourner AdGuard Home ni de servir le DHCP/DNS d'un foyer.
- **Modèle recommandé : Raspberry Pi 4 (2 Go).** Pi 3B+ acceptable, Pi 5 pour de
  la marge.
- **Connexion filaire (Ethernet) obligatoire** pour le boîtier : il sert le
  DHCP/DNS de toute la maison, la fiabilité prime sur le Wi-Fi. Cela **exclut le
  Pi Zero** (pas d'Ethernet natif).
- **Écran : HAT e-paper Waveshare (2.9" ou 4.2")**, connecté en SPI sur le GPIO,
  piloté directement par la Pi.

## Conséquences

- ✅ Une seule carte fait tout : moteur, écran, agent, mises à jour.
- ✅ Support logiciel mature (Raspberry Pi OS, bibliothèques e-paper).
- ⚠️ L'e-paper a un **rafraîchissement lent** : affichage semi-statique
  (compteurs, statut), pas d'animation. Utiliser le rafraîchissement partiel.
- ⚠️ Coût matériel plus élevé qu'un microcontrôleur, mais l'écart est marginal
  au regard du coût total du boîtier (Pi + écran + carte SD + boîtier + alim).
- 💡 Un ESP32 ne redeviendrait pertinent que pour un **afficheur déporté sans
  fil** — hors périmètre du boîtier unique actuel.
