"""Client de l'API REST d'AdGuard Home.

On ne réimplémente pas le DNS : l'agent lit les statistiques et l'état, et pilote
le serveur DHCP, via l'API locale d'AdGuard Home (voir ADR-0001 et ADR-0003).

Authentification : AdGuard Home utilise une **session par cookie** obtenue via
``POST /control/login``. Le client se connecte à la demande, une seule fois, puis
réutilise le cookie de session pour les appels suivants.
"""

from __future__ import annotations

import httpx

from hestia.adguard.models import DhcpConfig, DhcpStatus, Stats, Status


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
        client: httpx.Client | None = None,
    ) -> None:
        self._username = username
        self._password = password
        self._authenticated = not username  # instance sans authentification
        self._client = client or httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> AdGuardClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    # -- Authentification ---------------------------------------------------

    def _login(self) -> None:
        try:
            response = self._client.post(
                "/control/login",
                json={"name": self._username, "password": self._password},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise AdGuardError(f"échec de connexion à AdGuard Home : {exc}") from exc
        self._authenticated = True  # le cookie de session est stocké dans le client

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        if not self._authenticated:
            self._login()
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise AdGuardError(f"{method} {path} a échoué : {exc}") from exc
        return response

    # -- Lecture ------------------------------------------------------------

    def get_stats(self) -> Stats:
        """Statistiques de filtrage (``GET /control/stats``)."""

        return Stats.from_api(self._request("GET", "/control/stats").json())

    def get_status(self) -> Status:
        """État d'AdGuard Home (``GET /control/status``)."""

        return Status.from_api(self._request("GET", "/control/status").json())

    def is_protection_enabled(self) -> bool:
        return self.get_status().protection_enabled

    def get_dhcp_status(self) -> DhcpStatus:
        """État du serveur DHCP (``GET /control/dhcp/status``)."""

        return DhcpStatus.from_api(self._request("GET", "/control/dhcp/status").json())

    # -- Écriture -----------------------------------------------------------

    def configure_dhcp(self, config: DhcpConfig) -> None:
        """Active et configure le serveur DHCP (``POST /control/dhcp/set_config``)."""

        self._request("POST", "/control/dhcp/set_config", json=config.to_api())
