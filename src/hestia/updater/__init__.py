"""Mises à jour OTA « maison » (voir ADR-0005).

Cycle : source GitHub → comparaison de version → téléchargement → vérification
de signature Ed25519 → installation atomique avec rollback.
"""

from hestia.updater.installer import Installer, InstallPaths, current_version
from hestia.updater.models import Release, UpdateResult, UpdateStatus
from hestia.updater.runner import UpdateRunner
from hestia.updater.signing import verify_signature
from hestia.updater.sources import GitHubReleaseSource, select_release
from hestia.updater.versions import is_newer, parse

__all__ = [
    "Installer",
    "InstallPaths",
    "current_version",
    "Release",
    "UpdateResult",
    "UpdateStatus",
    "UpdateRunner",
    "verify_signature",
    "GitHubReleaseSource",
    "select_release",
    "is_newer",
    "parse",
]
