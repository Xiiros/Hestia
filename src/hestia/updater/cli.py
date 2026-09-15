"""Point d'entrée du service de mise à jour (``hestia-update``).

Lancé périodiquement (timer systemd). Assemble la source GitHub, l'installateur
et le vérificateur de signature à partir de la configuration, puis exécute un
cycle de mise à jour.
"""

from __future__ import annotations

from pathlib import Path

import httpx

from hestia import __version__
from hestia.settings import Settings, load_settings
from hestia.updater.installer import Installer, InstallPaths
from hestia.updater.models import UpdateResult
from hestia.updater.runner import UpdateRunner
from hestia.updater.signing import load_public_key
from hestia.updater.sources import GitHubReleaseSource


def _http_downloader(url: str) -> bytes:
    return httpx.get(url, follow_redirects=True, timeout=30.0).raise_for_status().content


def default_health_check(release_dir: Path) -> bool:
    """Contrôle de santé minimal après installation.

    À enrichir : redémarrer le service Hestia et vérifier qu'il répond (voir
    ADR-0005). Pour l'instant, on vérifie simplement que la release a bien été
    déployée.
    """

    return release_dir.is_dir() and any(release_dir.iterdir())


def build_runner(settings: Settings) -> UpdateRunner:
    source = GitHubReleaseSource(settings.update.repo, settings.update.asset_suffix)
    installer = Installer(
        InstallPaths(Path(settings.update.install_root)),
        health_check=default_health_check,
    )
    public_key = load_public_key(settings.update.public_key_path)
    return UpdateRunner(
        source,
        installer,
        public_key,
        _http_downloader,
        channel=settings.update.channel,
    )


def main(argv: list[str] | None = None) -> int:
    settings = load_settings()
    result: UpdateResult = build_runner(settings).run_once(__version__)
    print(f"[hestia-update] {result.status} (depuis {result.from_version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
