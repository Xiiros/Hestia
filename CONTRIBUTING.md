# Contribuer à Hestia

Ce document décrit comment on travaille sur le code : branches, commits, revues
et fusions. Pour tout ce qui concerne la sortie des versions et leur déploiement
sur les Raspberry Pi, voir [`docs/RELEASING.md`](docs/RELEASING.md).

Contexte : Hestia est un logiciel de protection de la vie privée qui tourne sur
des appareils placés chez des particuliers et qui **se mettent à jour tout
seuls**. Une release cassée part sur du matériel distant, difficile à récupérer.
La rigueur du processus n'est pas de la bureaucratie : c'est ce qui protège la
flotte et la confiance des utilisateurs.

## Vue d'ensemble

```
  feat/ma-fonctionnalite ──PR──▶ main ──▶ release/1.3 ──tag v1.3.0──▶ flotte
        (branche courte)        (toujours     (stabilisation)
                                 livrable)
```

- **`main`** : toujours dans un état livrable. Personne ne pousse dessus
  directement, tout passe par une Pull Request.
- **Branches de travail** : courtes, une par changement, supprimées après fusion.
- **Branches de release** (`release/X.Y`) : créées au moment de sortir une
  version, on n'y met plus que des corrections.

## Branches

Nomme tes branches par un préfixe qui dit l'intention :

| Préfixe      | Usage                                  | Exemple                     |
|--------------|----------------------------------------|-----------------------------|
| `feat/`      | nouvelle fonctionnalité                | `feat/chiffrement-dns`      |
| `fix/`       | correction de bug                      | `fix/fuite-memoire`         |
| `chore/`     | maintenance, outillage                 | `chore/maj-dependances`     |
| `docs/`      | documentation                          | `docs/guide-installation`   |

Garde-les courtes (quelques jours). Une grosse fonctionnalité se découpe en
plusieurs petites PR plutôt qu'en une branche qui vit des semaines.

## Commits — Conventional Commits

On utilise [Conventional Commits](https://www.conventionalcommits.org/fr/). Le
message de commit détermine **automatiquement** le prochain numéro de version et
alimente le `CHANGELOG.md`. Format :

```
<type>(<portée facultative>): <description à l'impératif>
```

Types utilisés :

| Type       | Effet sur la version | Pour…                                    |
|------------|----------------------|------------------------------------------|
| `feat`     | mineure (0.**X**.0)  | une nouvelle fonctionnalité              |
| `fix`      | patch (0.0.**X**)    | une correction de bug                    |
| `perf`     | patch                | une amélioration de performance          |
| `refactor` | aucune               | refactorisation sans changement visible  |
| `docs`     | aucune               | documentation                            |
| `test`     | aucune               | ajout ou correction de tests             |
| `build`    | aucune               | build, dépendances                       |
| `ci`       | aucune               | intégration continue                     |
| `chore`    | aucune               | divers, maintenance                      |

**Rupture de compatibilité** (bump **majeur**) : ajoute un `!` après le type,
ou une ligne `BREAKING CHANGE:` dans le corps du message.

```
feat!: change le format du fichier de configuration

BREAKING CHANGE: l'ancien hestia.conf n'est plus lu, migrer vers hestia.toml.
```

Exemples :

```
feat(reseau): ajoute le blocage des traqueurs par liste
fix(maj): corrige le rollback quand l'espace disque est plein
docs: complète le guide d'installation Raspberry Pi
```

## Pull Requests & fusion

1. Pousse ta branche et ouvre une **Pull Request vers `main`**.
2. Le **titre de la PR** doit respecter les Conventional Commits (la CI le
   vérifie) : c'est lui qui deviendra le message de commit.
3. Au moins **une relecture** est requise, et la **CI doit être verte**.
4. On fusionne en **squash** : toute la PR devient **un seul commit propre** sur
   `main`. La branche est ensuite supprimée.

Pourquoi le squash : un historique de `main` lisible (1 fonctionnalité = 1 ligne)
et un `revert` simple si un changement pose problème sur la flotte.

### Protection de `main` (à activer dans les réglages GitHub)

À configurer une fois dans **Settings → Branches → Add rule** sur `main` (et
idéalement `release/**`) :

- ✅ Require a pull request before merging → **Require 1 approval**
- ✅ Require status checks to pass → cocher **CI / Titre de PR** et **CI / Lint & tests**
- ✅ Require branches to be up to date before merging
- ✅ Require linear history (cohérent avec le squash)
- ✅ Do not allow bypassing the above settings

## Résumé express

```bash
git switch main && git pull
git switch -c feat/ma-fonctionnalite
# … travail …
git commit -m "feat: décrit le changement"
git push -u origin feat/ma-fonctionnalite
# ouvrir la PR sur GitHub, faire relire, fusionner en squash
```
