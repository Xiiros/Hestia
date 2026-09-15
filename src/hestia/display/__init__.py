"""Couche d'affichage : une interface commune, plusieurs rendus."""

from hestia.display.base import Display, Screen
from hestia.display.console import ConsoleDisplay

__all__ = ["Display", "Screen", "ConsoleDisplay", "build_display"]


def build_display(kind: str) -> Display:
    """Fabrique le rendu voulu (``console`` en dev, ``epaper`` sur la Pi)."""

    if kind == "console":
        return ConsoleDisplay()
    if kind == "epaper":
        # Import tardif : le pilote e-paper n'existe que sur la Raspberry Pi.
        from hestia.display.epaper import EPaperDisplay

        return EPaperDisplay()
    raise ValueError(f"type d'écran inconnu : {kind!r}")
