"""Construction des écrans à partir des données métier."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hestia.adguard.models import Stats
from hestia.display.base import Screen

if TYPE_CHECKING:
    from hestia.onboarding.tutorials import Tutorial


def dashboard(stats: Stats, *, protection_on: bool = True) -> Screen:
    """Tableau de bord principal."""

    etat = "actif" if protection_on else "INACTIF"
    return Screen(
        title="Hestia",
        lines=[
            f"Protection : {etat}",
            f"Requetes   : {stats.num_dns_queries}",
            f"Bloquees   : {stats.num_blocked_filtering}",
            f"Taux       : {stats.blocked_percentage} %",
        ],
    )


def onboarding_conflict(tutorial: Tutorial, server_ip: str) -> Screen:
    """Écran affiché quand un DHCP concurrent est détecté.

    L'écran e-paper étant petit, on affiche l'essentiel (le problème, la box
    détectée, l'adresse d'administration) et on renvoie vers le tutoriel complet.
    """

    return Screen(
        title="Action requise",
        lines=[
            "Un autre DHCP est actif sur",
            f"votre reseau ({server_ip}).",
            "",
            f"Box detectee : {tutorial.box_name}",
            f"Admin : {tutorial.admin_url}",
            "",
            "Desactivez son DHCP pour",
            "activer Hestia (voir guide).",
        ],
    )
