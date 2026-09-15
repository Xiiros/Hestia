"""Couche d'affichage : une interface commune, plusieurs rendus."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from hestia.display.base import Display, Screen
from hestia.display.console import ConsoleDisplay

if TYPE_CHECKING:
    from hestia.settings import DisplaySettings

__all__ = ["Display", "Screen", "ConsoleDisplay", "build_display"]


def build_display(settings: DisplaySettings) -> Display:
    """Fabrique le rendu voulu selon la configuration.

    - ``console`` : rendu texte dans le terminal (dev) ;
    - ``png``     : rendu dans un fichier PNG (prévisualisation sans matériel) ;
    - ``epaper``  : écran e-paper Waveshare (Raspberry Pi).
    """

    if settings.kind == "console":
        return ConsoleDisplay()

    # Import tardif : ces rendus dépendent de Pillow (extra « hardware »).
    from hestia.display.render import DisplaySpec

    spec = DisplaySpec(
        width=settings.width,
        height=settings.height,
        font_path=settings.font_path or None,
    )

    if settings.kind == "png":
        from hestia.display.png import PngDisplay

        return PngDisplay(spec, Path(settings.png_path))

    if settings.kind == "epaper":
        from hestia.display.epaper import EPaperDisplay

        return EPaperDisplay(spec, settings.model)

    raise ValueError(f"type d'écran inconnu : {settings.kind!r}")
