"""Client minimal de l'API REST d'AdGuard Home.

On ne réimplémente pas le DNS : l'agent lit les statistiques et l'état via
l'API locale d'AdGuard Home (voir ADR-0001 et ADR-0003).
"""

from __future__ import annotations

import httpx

from hestia.adguard.models import Stats


class AdGuardError(RuntimeError):
    """Erreur de communication avec AdGuard Home."""


class AdGuardClient:
    def __init__(
        self,
        base_url: str,
        username: str = "",
        password: str = "",
        *,
        timeout: float = 5.0,
    ) -> None:
        auth = httpx.BasicAuth(username, password) if username else None
        self._client = httpx.Client(base_url=base_url.rstrip("/"), auth=auth, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> AdGuardClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def get_stats(self) -> Stats:
        """Récupère les statistiques de filtrage (``GET /control/stats``)."""

        try:
            response = self._client.get("/control/stats")
            response.raise_for_status()
        except httpx.HTTPError as exc:  # réseau, statut HTTP, timeout…
            raise AdGuardError(f"échec de récupération des stats : {exc}") from exc
        return Stats.from_api(response.json())

    def is_protection_enabled(self) -> bool:
        """Indique si la protection DNS est active (``GET /control/status``)."""

        try:
            response = self._client.get("/control/status")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise AdGuardError(f"échec de récupération du statut : {exc}") from exc
        return bool(response.json().get("protection_enabled", False))
