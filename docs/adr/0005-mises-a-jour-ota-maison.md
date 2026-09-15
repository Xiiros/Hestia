# ADR-0005 — Mises à jour à distance : OTA « maison »

- **Statut** : Accepté
- **Date** : 2026-09-15

## Contexte

Les boîtiers sont installés chez des particuliers et doivent se mettre à jour
**automatiquement**. Une release défectueuse part sur du matériel distant,
difficile à récupérer. Options envisagées : une solution « maison » (nos propres
scripts + releases GitHub), ou une plateforme OTA (balenaCloud, Mender, RAUC).

## Décision

On implémente une **solution de mise à jour maison**, sans plateforme externe.

Principe :
- Les versions sont publiées comme **releases GitHub signées** (le workflow
  `release.yml` existe déjà).
- Un service `systemd` **updater** sur chaque Pi vérifie périodiquement le canal
  auquel elle est abonnée (**beta** ou **stable**), télécharge la version, en
  **vérifie la signature**, puis l'applique.
- Après application, un **contrôle de santé** valide le boîtier ; en cas d'échec,
  **retour à la version précédente** (rollback).
- Diffusion par **paliers** (rollout progressif) sur le canal stable.

## Conséquences

- ✅ Aucune dépendance à une plateforme tierce ; maîtrise totale de la chaîne.
- ✅ S'appuie sur l'outillage déjà en place (branches de release, tags, canaux).
- ⚠️ **À notre charge** d'implémenter correctement : signature des artefacts,
  vérification côté appareil, contrôle de santé et mécanisme de rollback fiable.
  Ce sont des points sensibles à ne pas bâcler.
- ⚠️ Le rollback suppose de **conserver la version précédente** sur l'appareil
  (espace disque, ou stratégie A/B à concevoir).
- 💡 Réévaluer une plateforme (balena/Mender) si la flotte grossit fortement ou
  si la maintenance du système maison devient trop lourde (nouvel ADR).
