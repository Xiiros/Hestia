"""Mise à jour OTA « maison ».

Squelette : la version est comparée à la dernière release publiée sur le canal
choisi (beta/stable). L'application réelle (téléchargement, **vérification de
signature**, contrôle de santé, rollback) reste à implémenter — ce sont les
points sensibles décrits dans ADR-0005.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class UpdateInfo:
    current: str
    latest: str

    @property
    def update_available(self) -> bool:
        return _parse(self.latest) > _parse(self.current)


def _parse(version: str) -> tuple[int, ...]:
    """Transforme « 1.4.2 » en (1, 4, 2) pour comparer deux versions SemVer."""

    core = version.lstrip("v").split("+")[0].split("-")[0]
    return tuple(int(part) for part in core.split("."))


def check_for_update(current: str, latest: str) -> UpdateInfo:
    """Compare la version courante à la dernière release du canal.

    Le paramètre ``latest`` sera fourni par un appel à l'API des releases GitHub
    (à brancher). Isolé ainsi, la comparaison de versions reste testable.
    """

    return UpdateInfo(current=current, latest=latest)


def apply_update(info: UpdateInfo) -> None:  # pragma: no cover - à implémenter
    """Télécharge, vérifie la signature, applique, contrôle la santé, rollback."""

    raise NotImplementedError(
        "Application OTA à implémenter : téléchargement signé + rollback (ADR-0005)."
    )
