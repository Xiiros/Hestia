"""Rendu e-paper (Waveshare).

Stub structuré : le pilote Waveshare et Pillow ne sont présents que sur la
Raspberry Pi (extra ``hardware``). Le rendu réel (buffer d'image, SPI) sera
implémenté ici. On garde une classe importable qui échoue explicitement si les
dépendances matérielles manquent, plutôt que de casser l'import du paquet.
"""

from __future__ import annotations

from hestia.display.base import Display, Screen


class EPaperDisplay(Display):
    def __init__(self) -> None:
        try:
            from PIL import Image, ImageDraw, ImageFont  # noqa: F401
        except ImportError as exc:  # pragma: no cover - dépend du matériel
            raise RuntimeError(
                "Pillow est requis pour l'écran e-paper : installez l'extra "
                "« hardware » (uv sync --extra hardware) sur la Raspberry Pi."
            ) from exc
        # TODO: initialiser le pilote Waveshare (epd = epdX.EPD(); epd.init()).

    def show(self, screen: Screen) -> None:  # pragma: no cover - dépend du matériel
        # TODO: dessiner `screen` dans une image PIL et l'envoyer au panneau
        # (rafraîchissement partiel pour les mises à jour fréquentes du tableau
        # de bord, complet pour les changements d'écran).
        raise NotImplementedError("rendu e-paper à implémenter sur la Raspberry Pi")
