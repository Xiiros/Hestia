"""Modèles de données de la mise à jour OTA."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class UpdateStatus(StrEnum):
    UP_TO_DATE = "up_to_date"  # rien de plus récent
    NO_RELEASE = "no_release"  # aucune release sur le canal
    BAD_SIGNATURE = "bad_signature"  # signature invalide -> refusé
    APPLIED = "applied"  # installée et validée
    ROLLED_BACK = "rolled_back"  # échec du contrôle de santé -> retour arrière


@dataclass(frozen=True, slots=True)
class Release:
    """Une release publiée, prête à être téléchargée."""

    version: str
    tag: str
    prerelease: bool
    artifact_url: str
    signature_url: str


@dataclass(frozen=True, slots=True)
class UpdateResult:
    status: UpdateStatus
    from_version: str
    to_version: str | None = None

    @property
    def changed(self) -> bool:
        return self.status == UpdateStatus.APPLIED
