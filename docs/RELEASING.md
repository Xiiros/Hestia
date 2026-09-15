# Sortir une version de Hestia

Ce guide décrit comment on passe de `main` à une version installée sur les
Raspberry Pi de la flotte. Il complète [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Principes

- **Versionnage sémantique** : `MAJEUR.MINEUR.CORRECTIF` (ex. `1.3.0`). La
  version est stockée dans le fichier [`VERSION`](../VERSION) et embarquée dans
  le build, pour que chaque Pi sache exactement ce qu'elle exécute.
- **Le numéro de version est calculé automatiquement** à partir des commits
  Conventional Commits (voir CONTRIBUTING.md).
- **Versions planifiées** : on sort une version à un jalon décidé, pas à chaque
  merge.
- **On ne pousse jamais une nouvelle version sur 100 % de la flotte d'un coup.**

## Les canaux

| Canal    | Appareils                     | Rôle                                   |
|----------|-------------------------------|----------------------------------------|
| `beta`   | tes Pi de test / volontaires  | valider une version avant diffusion    |
| `stable` | les Pi des particuliers       | la version de production, diffusée par paliers |

Rien n'atteint `stable` sans être passé par `beta`.

## Processus normal

### 1. Préparer la branche de release

Depuis GitHub : **Actions → « Préparer une release » → Run workflow**, en
choisissant le type d'incrément (`auto` recommandé).

Le workflow :
- calcule la prochaine version à partir des commits,
- crée la branche `release/X.Y`,
- met à jour `VERSION` et `CHANGELOG.md`,
- pousse la branche.

> À partir d'ici, `main` peut continuer d'avancer (nouvelles fonctionnalités)
> sans impacter la version en cours de préparation.

### 2. Stabiliser

Sur `release/X.Y`, **uniquement des corrections** (`fix:`), via PR. Pas de
nouvelle fonctionnalité. On construit l'image et on la déploie sur le canal
**beta** pour tester sur du vrai matériel.

### 3. Publier

Quand la beta est validée, on pose le tag — c'est lui qui déclenche la Release :

```bash
git switch release/1.3 && git pull
git tag v1.3.0
git push origin v1.3.0
```

Le workflow **Release** génère les notes de version et crée la Release GitHub.
Le déploiement vers `stable` se fait ensuite **par paliers** (rollout progressif,
ex. 5 % → 25 % → 100 %), en surveillant la santé des appareils entre chaque
palier.

### 4. Reporter sur main

Ramener la correction du numéro de version et les fixes faits sur la release
vers `main` (fusion de `release/X.Y` dans `main` via PR), pour qu'ils ne soient
pas perdus.

## Corriger une version déjà en production (hotfix)

Un bug critique est découvert sur les Pi alors que `main` contient déjà du
travail en cours qu'on ne veut pas embarquer :

```bash
git switch release/1.3 && git pull
git switch -c fix/probleme-critique
# … correction …
git commit -m "fix: corrige le problème critique"
# PR vers release/1.3, relecture, squash
```

Puis on incrémente le patch et on publie :

```bash
git switch release/1.3 && git pull
git tag v1.3.1
git push origin v1.3.1
```

On teste sur **beta**, on diffuse par paliers sur **stable**, puis on reporte le
fix sur `main`.

## Garde-fous pour une flotte auto-update

Ces points relèvent de l'infrastructure de mise à jour (au-delà de Git), mais ils
conditionnent le processus ci-dessus :

- **Signature** : les artefacts de mise à jour doivent être signés ; une Pi
  n'installe que ce qui est authentique. Indispensable pour du logiciel de vie
  privée.
- **Rollback** : une Pi doit pouvoir revenir à la version précédente si la
  nouvelle ne démarre pas ou échoue un contrôle de santé.
- **Rollout progressif** : jamais 100 % d'un coup ; on élargit palier par palier
  en surveillant.
- **Health-check post-mise à jour** : chaque Pi confirme qu'elle est saine après
  application ; un pic d'échecs stoppe le rollout.

Ces étapes sont marquées `TODO` dans `.github/workflows/release.yml`, à brancher
sur votre serveur de mise à jour le moment venu.
