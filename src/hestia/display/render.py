"""Rendu d'un écran vers une image, indépendant du modèle d'écran.

Le même rendu alimente l'afficheur PNG de test et l'écran e-paper réel : seule la
sortie diffère (fichier PNG vs panneau physique). L'image est en mode « 1 »
(1 bit, noir et blanc) pour coller aux e-paper monochromes.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from hestia.display.base import Screen

_WHITE = 1
_BLACK = 0


@dataclass(slots=True, frozen=True)
class DisplaySpec:
    """Géométrie de l'écran (indépendante du pilote). Taille configurable."""

    width: int = 250  # 2.13" Waveshare par défaut ; ajustable selon le modèle
    height: int = 122
    margin: int = 6
    title_font_size: int = 20
    line_font_size: int = 16
    line_spacing: int = 4
    font_path: str | None = None  # TTF ; sinon police par défaut de Pillow


def _load_font(path: str | None, size: int) -> ImageFont.ImageFont:
    if path:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1 : pas de taille pour la police par défaut
        return ImageFont.load_default()


def _text_height(font: ImageFont.ImageFont) -> int:
    top, bottom = font.getbbox("Ayg")[1], font.getbbox("Ayg")[3]
    return bottom - top


def render_screen(screen: Screen, spec: DisplaySpec) -> Image.Image:
    """Dessine ``screen`` dans une image de la taille de ``spec``."""

    image = Image.new("1", (spec.width, spec.height), _WHITE)
    draw = ImageDraw.Draw(image)

    title_font = _load_font(spec.font_path, spec.title_font_size)
    line_font = _load_font(spec.font_path, spec.line_font_size)

    x = spec.margin
    y = spec.margin

    draw.text((x, y), screen.title, font=title_font, fill=_BLACK)
    y += _text_height(title_font) + spec.line_spacing
    draw.line([(x, y), (spec.width - spec.margin, y)], fill=_BLACK)
    y += spec.line_spacing

    line_height = _text_height(line_font) + spec.line_spacing
    for line in screen.lines:
        if y + line_height > spec.height:
            break  # on ne déborde pas de l'écran
        draw.text((x, y), line, font=line_font, fill=_BLACK)
        y += line_height

    return image
