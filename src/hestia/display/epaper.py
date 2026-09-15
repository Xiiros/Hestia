"""Rendu e-paper (Waveshare).

Le dessin est **indépendant du modèle** (via ``render_screen``) ; seule la
liaison au pilote dépend du modèle, choisie par configuration
(``display.model``, ex. ``epd2in13_V4``). Le pilote Waveshare (paquet
``waveshare_epd``) est fourni sur la Raspberry Pi, hors de ce dépôt.
"""

from __future__ import annotations

from importlib import import_module

from hestia.display.base import Display, Screen
from hestia.display.render import DisplaySpec, render_screen


class EPaperDisplay(Display):
    def __init__(self, spec: DisplaySpec, model: str) -> None:
        self._spec = spec
        self._model = model
        try:
            from PIL import Image  # noqa: F401
        except ImportError as exc:  # pragma: no cover - dépend du matériel
            raise RuntimeError(
                "Pillow est requis pour l'écran e-paper : installez l'extra "
                "« hardware » (uv sync --extra hardware)."
            ) from exc
        self._epd = self._load_panel(model)
        self._epd.init()

    @staticmethod
    def _load_panel(model: str):  # pragma: no cover - dépend du pilote Waveshare
        try:
            module = import_module(f"waveshare_epd.{model}")
        except ImportError as exc:
            raise RuntimeError(
                f"Pilote e-paper introuvable pour le modèle {model!r}. Installez la "
                "bibliothèque waveshare_epd sur la Raspberry Pi."
            ) from exc
        return module.EPD()

    def show(self, screen: Screen) -> None:  # pragma: no cover - dépend du matériel
        image = render_screen(screen, self._spec)
        # getbuffer/display sont fournis par le pilote Waveshare.
        self._epd.display(self._epd.getbuffer(image))

    def clear(self) -> None:  # pragma: no cover - dépend du matériel
        self._epd.Clear()
