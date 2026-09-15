# Mises à jour OTA

Chaîne de bout en bout des mises à jour à distance (voir
[ADR-0005](adr/0005-mises-a-jour-ota-maison.md)).

## Le principe en une image

```
  Équipe                     GitHub                     Raspberry Pi (flotte)
  ──────                     ──────                     ─────────────────────
  tag vX.Y.Z  ──► release.yml : build + SIGNE l'artefact
                             │  hestia-vX.Y.Z.tar.gz (+ .sig)
                             ▼
                       Release GitHub  ──►  hestia-update (timer horaire)
                                              1. cherche la dernière release du canal
                                              2. compare la version
                                              3. télécharge artefact + signature
                                              4. VÉRIFIE la signature (clé publique)
                                              5. installe (lien atomique) + contrôle
                                                 de santé, sinon ROLLBACK
```

## Clés de signature

Seule la clé **publique** est sur les boîtiers ; la clé **privée** ne quitte
jamais les secrets CI. Générer la paire une fois :

```bash
./scripts/generate-update-key.sh
```

- `update-key.pem` (privée) → secret GitHub **`UPDATE_SIGNING_KEY`**.
- `update-key.pub` (publique) → `/etc/hestia/update-key.pub` sur chaque Pi.

Sans clé configurée, la CI publie un artefact **non signé** que les appareils
**refusent** (une paire artefact + `.sig` est exigée). La sécurité ne dépend
donc pas d'une bonne volonté : pas de signature valide, pas d'installation.

## Canaux

- Tag `vX.Y.Z` → release stable → canal **stable**.
- Tag `vX.Y.Z-beta.N` → pré-version → canal **beta** uniquement.

Chaque Pi suit le canal défini par `update.channel` (voir la configuration).
On valide d'abord sur des Pi **beta** avant de diffuser sur **stable**, par
paliers (rollout progressif) — cette diffusion par paliers est gérée côté
serveur/relais de distribution, hors de ce dépôt.

## Côté appareil

Le service `hestia-update` (déclenché par `hestia-updater.timer`, avec délai
aléatoire pour étaler la charge sur la flotte) exécute un cycle complet. Les
versions sont installées dans `<install_root>/releases/<version>/` et un lien
`current` pointe vers la version active : la bascule est atomique et réversible.

## Ce qui reste à finaliser sur la Raspberry Pi

- **Contrôle de santé réel** : aujourd'hui minimal (la release est déployée).
  À enrichir : redémarrer le service et vérifier qu'il répond avant de valider.
- **Construction de l'image** : l'artefact actuel est l'arbre source ; la
  fabrication de l'image/venv de la Pi reste à brancher.
