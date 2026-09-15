"""Orchestration du premier démarrage.

Détecte un serveur DHCP concurrent ; si présent, identifie la box et prépare le
tutoriel adapté à afficher. La détection réseau est injectable (``probe``) afin
de pouvoir tester le flux sans matériel.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from hestia.display import Display
from hestia.display.views import onboarding_conflict
from hestia.onboarding.tutorials import Tutorial, tutorial_for
from hestia.system.dhcp import DhcpServer, find_foreign_servers
from hestia.system.vendors import guess_isp

# Signature d'une sonde DHCP : (interface, timeout) -> serveurs détectés.
ProbeFn = Callable[[str, float], list[DhcpServer]]


@dataclass(slots=True)
class OnboardingResult:
    """Résultat de l'étape de premier démarrage."""

    conflict: bool
    server: DhcpServer | None = None
    tutorial: Tutorial | None = None


def _admin_url(server_ip: str) -> str:
    return f"http://{server_ip}"


def check_dhcp_conflict(
    probe: ProbeFn,
    interface: str,
    own_mac: str,
    own_ips: Iterable[str],
    timeout: float = 5.0,
) -> OnboardingResult:
    """Sonde le réseau et prépare un tutoriel si un DHCP concurrent répond."""

    servers = probe(interface, timeout)
    foreign = find_foreign_servers(servers, own_mac, own_ips)
    if not foreign:
        return OnboardingResult(conflict=False)

    server = foreign[0]
    isp = guess_isp(server.mac)
    tutorial = tutorial_for(isp, _admin_url(server.server_ip))
    return OnboardingResult(conflict=True, server=server, tutorial=tutorial)


def run_first_boot(
    display: Display,
    probe: ProbeFn,
    interface: str,
    own_mac: str,
    own_ips: Iterable[str],
    timeout: float = 5.0,
) -> OnboardingResult:
    """Exécute la détection et affiche le guide si nécessaire."""

    result = check_dhcp_conflict(probe, interface, own_mac, own_ips, timeout)
    if result.conflict and result.server and result.tutorial:
        display.show(onboarding_conflict(result.tutorial, result.server.server_ip))
    return result
