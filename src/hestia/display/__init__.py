"""Couche d'affichage : une interface commune, plusieurs rendus."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from hestia.display.base import Display, Screen
from hestia.display.console import ConsoleDisplay

if TYPE_CHECKING:
    from hestia.settings import DisplaySettings

__all__ = ["Display", "Screen", "ConsoleDisplay", "build_display", "choose_display"]


def _warn(message: str) -> None:
    print(f"[hestia] {message}")


def choose_display(candidates: list[tuple[str, Callable[[], Display]]]) -> Display:
    """Essaie chaque fabrique dans l'ordre ; renvoie le premier écran construit.

    Permet la bascule automatique e-paper → fenêtre bureau → console : une
    fabrique qui échoue (matériel absent, pas d'affichage graphique…) est
    signalée, et on passe à la suivante.
    """

    last_exc: Exception | None = None
    for label, factory in candidates:
        try:
            return factory()
        except Exception as exc:  # matériel/pilote/affichage indisponible
            last_exc = exc
            _warn(f"écran « {label} » indisponible : {exc}")
    raise last_exc or RuntimeError("aucun écran disponible")


def build_display(settings: DisplaySettings) -> Display:
    """Fabrique le rendu voulu selon la configuration.

    - ``console`` : rendu texte dans le terminal (dev) ;
    - ``png``     : rendu dans un fichier PNG (prévisualisation sans matériel) ;
    - ``window``  : fenêtre sur le bureau (repli sur console si pas d'affichage) ;
    - ``epaper``  : écran e-paper Waveshare ; **si non détecté, bascule sur une
      fenêtre bureau, puis sur la console**.
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

    if settings.kind == "window":
        from hestia.display.window import WindowDisplay

        return choose_display(
            [
                ("window", lambda: WindowDisplay(spec)),
                ("console", ConsoleDisplay),
            ]
        )

    if settings.kind == "epaper":
        from hestia.display.epaper import EPaperDisplay
        from hestia.display.window import WindowDisplay

        return choose_display(
            [
                ("epaper", lambda: EPaperDisplay(spec, settings.model)),
                ("window", lambda: WindowDisplay(spec)),
                ("console", ConsoleDisplay),
            ]
        )

    raise ValueError(f"type d'écran inconnu : {settings.kind!r}")
