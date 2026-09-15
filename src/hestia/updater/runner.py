"""Orchestration d'un cycle de mise à jour.

Enchaîne : recherche de la dernière release du canal → comparaison de version →
téléchargement → **vérification de signature** → installation avec rollback.
Le téléchargement est injectable pour rester testable sans réseau.
"""

from __future__ import annotations

from collections.abc import Callable

from hestia.updater.installer import Installer
from hestia.updater.models import Release, UpdateResult, UpdateStatus
from hestia.updater.signing import verify_signature
from hestia.updater.versions import is_newer

# Télécharge une URL et renvoie son contenu.
Downloader = Callable[[str], bytes]


class ReleaseSource:
    """Contrat minimal d'une source de releases (cf. GitHubReleaseSource)."""

    def latest(self, channel: str) -> Release | None:  # pragma: no cover - protocole
        raise NotImplementedError


class UpdateRunner:
    def __init__(
        self,
        source: ReleaseSource,
        installer: Installer,
        public_key_pem: bytes,
        downloader: Downloader,
        *,
        channel: str = "stable",
    ) -> None:
        self._source = source
        self._installer = installer
        self._public_key = public_key_pem
        self._download = downloader
        self._channel = channel

    def run_once(self, current: str) -> UpdateResult:
        release = self._source.latest(self._channel)
        if release is None:
            return UpdateResult(UpdateStatus.NO_RELEASE, from_version=current)

        if not is_newer(release.version, current):
            return UpdateResult(UpdateStatus.UP_TO_DATE, from_version=current)

        artifact = self._download(release.artifact_url)
        signature = self._download(release.signature_url)
        if not verify_signature(artifact, signature, self._public_key):
            return UpdateResult(
                UpdateStatus.BAD_SIGNATURE, from_version=current, to_version=release.version
            )

        applied = self._installer.apply(release.version, artifact)
        status = UpdateStatus.APPLIED if applied else UpdateStatus.ROLLED_BACK
        return UpdateResult(status, from_version=current, to_version=release.version)
