"""Installation atomique d'une release, avec retour arrière.

Modèle « A/B » au niveau applicatif : chaque version est extraite dans
``<root>/releases/<version>/`` et un lien symbolique ``<root>/current`` pointe
vers la version active. Basculer = repointer le lien de façon atomique
(``os.replace``). En cas d'échec du contrôle de santé, on repointe vers la
version précédente (rollback).

La logique d'orchestration est isolée des effets de bord (extraction, contrôle
de santé) qui sont injectables, afin de rester testable sans vrai artefact.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

# Extrait l'artefact (octets) vers un dossier de destination.
Extractor = Callable[[bytes, Path], None]
# Valide une release installée (démarre-t-elle correctement ?).
HealthCheck = Callable[[Path], bool]


@dataclass(frozen=True, slots=True)
class InstallPaths:
    root: Path

    @property
    def releases_dir(self) -> Path:
        return self.root / "releases"

    @property
    def current_link(self) -> Path:
        return self.root / "current"

    def release_dir(self, version: str) -> Path:
        return self.releases_dir / version


def current_version(paths: InstallPaths) -> str | None:
    """Version actuellement active (cible du lien ``current``), ou ``None``."""

    link = paths.current_link
    if not link.is_symlink():
        return None
    return os.readlink(link).rstrip("/").rsplit("/", 1)[-1]


def _switch_current(paths: InstallPaths, version: str) -> None:
    """Repointe ``current`` vers ``version`` de façon atomique."""

    target = paths.release_dir(version)
    tmp = paths.current_link.with_name("current.tmp")
    if tmp.exists() or tmp.is_symlink():
        tmp.unlink()
    tmp.symlink_to(target)
    os.replace(tmp, paths.current_link)  # bascule atomique


def default_tar_extractor(data: bytes, dest: Path) -> None:  # pragma: no cover - I/O
    """Extraction d'un artefact ``.tar.gz`` vers ``dest`` (filtre de sécurité)."""

    import io
    import tarfile

    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        tar.extractall(dest, filter="data")  # refuse les chemins hors de dest


class Installer:
    def __init__(
        self,
        paths: InstallPaths,
        *,
        extractor: Extractor = default_tar_extractor,
        health_check: HealthCheck,
    ) -> None:
        self._paths = paths
        self._extract = extractor
        self._health_check = health_check

    def apply(self, version: str, artifact: bytes) -> bool:
        """Installe et active ``version`` ; rollback si le contrôle de santé échoue.

        Renvoie ``True`` si la nouvelle version est active et saine, ``False`` si
        elle a été rejetée et l'ancienne version restaurée.
        """

        previous = current_version(self._paths)

        release_dir = self._paths.release_dir(version)
        self._extract(artifact, release_dir)
        _switch_current(self._paths, version)

        if self._health_check(release_dir):
            return True

        # Échec : on revient à la version précédente si elle existe.
        if previous and previous != version:
            _switch_current(self._paths, previous)
        return False
