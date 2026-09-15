"""Source des releases : l'API GitHub.

La sélection de la release (``select_release``) est une fonction pure, testable
sans réseau ; seule la récupération HTTP dépend de httpx.
"""

from __future__ import annotations

import httpx

from hestia.updater.models import Release


def _find_asset_url(assets: list[dict], predicate) -> str:
    for asset in assets:
        name = asset.get("name", "")
        if predicate(name):
            return asset.get("browser_download_url", "")
    return ""


def select_release(
    releases: list[dict],
    channel: str,
    asset_suffix: str,
    signature_ext: str = ".sig",
) -> Release | None:
    """Choisit la release adaptée au canal parmi la réponse de l'API GitHub.

    - ``stable`` : la release publiée la plus récente qui n'est pas une pré-version ;
    - ``beta``   : la plus récente, pré-versions incluses.

    L'ordre de la liste suit celui de l'API (de la plus récente à la plus ancienne).
    Une release sans artefact correspondant (ou sans signature) est ignorée.
    """

    for release in releases:
        if release.get("draft"):
            continue
        if channel == "stable" and release.get("prerelease"):
            continue

        assets = release.get("assets", [])
        artifact_url = _find_asset_url(assets, lambda n: n.endswith(asset_suffix))
        signature_url = _find_asset_url(assets, lambda n: n.endswith(asset_suffix + signature_ext))
        if not artifact_url or not signature_url:
            continue

        tag = release.get("tag_name", "")
        return Release(
            version=tag.lstrip("vV"),
            tag=tag,
            prerelease=bool(release.get("prerelease")),
            artifact_url=artifact_url,
            signature_url=signature_url,
        )
    return None


class GitHubReleaseSource:
    """Récupère les releases publiées d'un dépôt via l'API GitHub."""

    def __init__(
        self,
        repo: str,
        asset_suffix: str,
        *,
        client: httpx.Client | None = None,
        timeout: float = 10.0,
    ) -> None:
        self._repo = repo
        self._asset_suffix = asset_suffix
        self._client = client or httpx.Client(base_url="https://api.github.com", timeout=timeout)

    def latest(self, channel: str) -> Release | None:
        response = self._client.get(f"/repos/{self._repo}/releases")
        response.raise_for_status()
        return select_release(response.json(), channel, self._asset_suffix)
