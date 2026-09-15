"""Modèles de données renvoyés par l'API AdGuard Home."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Stats:
    """Statistiques de filtrage affichées sur le tableau de bord."""

    num_dns_queries: int = 0
    num_blocked_filtering: int = 0

    @property
    def blocked_percentage(self) -> float:
        if self.num_dns_queries == 0:
            return 0.0
        return round(100 * self.num_blocked_filtering / self.num_dns_queries, 1)

    @classmethod
    def from_api(cls, payload: dict) -> Stats:
        """Construit un ``Stats`` depuis la réponse de ``GET /control/stats``."""

        return cls(
            num_dns_queries=int(payload.get("num_dns_queries", 0)),
            num_blocked_filtering=int(payload.get("num_blocked_filtering", 0)),
        )


@dataclass(slots=True, frozen=True)
class Status:
    """État d'AdGuard Home (``GET /control/status``)."""

    running: bool = False
    protection_enabled: bool = False
    version: str = ""

    @classmethod
    def from_api(cls, payload: dict) -> Status:
        return cls(
            running=bool(payload.get("running", False)),
            protection_enabled=bool(payload.get("protection_enabled", False)),
            version=str(payload.get("version", "")),
        )


@dataclass(slots=True, frozen=True)
class DhcpConfig:
    """Configuration du serveur DHCP v4 d'AdGuard Home.

    Modèle « remplacement du DHCP de la box » : Hestia distribue les baux, mais
    la passerelle (``gateway_ip``) reste la box (routeur Internet). Le DNS servi
    aux clients est Hestia elle-même — géré par AdGuard, pas ici.
    """

    interface: str
    gateway_ip: str
    subnet_mask: str
    range_start: str
    range_end: str
    lease_duration: int = 86400  # secondes

    def to_api(self) -> dict:
        """Sérialise vers le schéma attendu par ``POST /control/dhcp/set_config``."""

        return {
            "enabled": True,
            "interface_name": self.interface,
            "v4": {
                "gateway_ip": self.gateway_ip,
                "subnet_mask": self.subnet_mask,
                "range_start": self.range_start,
                "range_end": self.range_end,
                "lease_duration": self.lease_duration,
            },
            "v6": {},
        }


@dataclass(slots=True, frozen=True)
class DhcpStatus:
    """État du serveur DHCP d'AdGuard Home (``GET /control/dhcp/status``)."""

    enabled: bool = False
    interface: str = ""

    @classmethod
    def from_api(cls, payload: dict) -> DhcpStatus:
        return cls(
            enabled=bool(payload.get("enabled", False)),
            interface=str(payload.get("interface_name", "")),
        )
