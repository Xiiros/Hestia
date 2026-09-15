"""Boucle réelle du premier démarrage.

Tant qu'un serveur DHCP concurrent répond, on affiche le tutoriel de désactivation
adapté à la box et on re-sonde périodiquement. Dès que le conflit disparaît, on
affiche un écran de confirmation et on laisse l'agent démarrer normalement.

L'attente (``sleep``) et la sonde (``probe``) sont injectables pour tester la
boucle sans matériel ni temporisation réelle.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from pathlib import Path

from hestia.display import Display
from hestia.display.views import onboarding_conflict, onboarding_resolved
from hestia.onboarding.flow import ProbeFn, check_dhcp_conflict


def is_done(marker: Path) -> bool:
    """Vrai si le premier démarrage a déjà été validé (marqueur présent)."""

    return marker.exists()


def mark_done(marker: Path) -> None:
    """Écrit le marqueur de premier démarrage terminé."""

    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("ok\n", encoding="utf-8")


def resolve_dhcp_conflict(
    display: Display,
    probe: ProbeFn,
    interface: str,
    own_mac: str,
    own_ips: Iterable[str],
    *,
    poll_seconds: float = 15.0,
    timeout: float = 5.0,
    sleep: Callable[[float], None] = time.sleep,
    max_attempts: int | None = None,
) -> bool:
    """Boucle jusqu'à disparition du conflit DHCP.

    Renvoie ``True`` quand le réseau est libre (conflit résolu), ``False`` si
    ``max_attempts`` est atteint sans résolution (utile pour les tests / une
    borne de sécurité).
    """

    own_ips = list(own_ips)
    attempts = 0
    while True:
        result = check_dhcp_conflict(probe, interface, own_mac, own_ips, timeout)
        if not result.conflict:
            display.show(onboarding_resolved())
            return True

        assert result.server is not None and result.tutorial is not None
        display.show(onboarding_conflict(result.tutorial, result.server.server_ip))

        attempts += 1
        if max_attempts is not None and attempts >= max_attempts:
            return False
        sleep(poll_seconds)
