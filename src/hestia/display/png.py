"""Afficheur PNG de test : rend l'écran dans un fichier image.

Permet de prévisualiser exactement ce qui s'affichera sur l'e-paper (même moteur
de rendu, même taille), sans matériel.
"""

from __future__ import annotations

from pathlib import Path

from hestia.display.base import Display, Screen
from hestia.display.render import DisplaySpec, render_screen


class PngDisplay(Display):
    def __init__(self, spec: DisplaySpec, output_path: Path) -> None:
        self._spec = spec
        self._output_path = Path(output_path)

    def show(self, screen: Screen) -> None:
        image = render_screen(screen, self._spec)
        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(self._output_path)

    def clear(self) -> None:
        pass
