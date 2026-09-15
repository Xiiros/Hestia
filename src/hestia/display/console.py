"""Rendu console : utile en développement, sans matériel."""

from __future__ import annotations

from hestia.display.base import Display, Screen

_WIDTH = 40


class ConsoleDisplay(Display):
    """Affiche l'écran dans le terminal, encadré, pour simuler l'e-paper."""

    def show(self, screen: Screen) -> None:
        print("┌" + "─" * _WIDTH + "┐")
        print("│ " + screen.title[: _WIDTH - 2].ljust(_WIDTH - 2) + " │")
        print("├" + "─" * _WIDTH + "┤")
        for line in screen.lines or [""]:
            print("│ " + line[: _WIDTH - 2].ljust(_WIDTH - 2) + " │")
        print("└" + "─" * _WIDTH + "┘")

    def clear(self) -> None:
        print("\n" * 2)
