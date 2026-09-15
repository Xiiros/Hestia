"""Premier démarrage : détection d'un DHCP concurrent et guide de désactivation."""

from hestia.onboarding.firstboot import is_done, mark_done, resolve_dhcp_conflict
from hestia.onboarding.flow import OnboardingResult, check_dhcp_conflict, run_first_boot
from hestia.onboarding.tutorials import Tutorial, tutorial_for

__all__ = [
    "OnboardingResult",
    "run_first_boot",
    "check_dhcp_conflict",
    "Tutorial",
    "tutorial_for",
    "is_done",
    "mark_done",
    "resolve_dhcp_conflict",
]
