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
