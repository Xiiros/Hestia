"""Interface d'affichage indépendante du matériel."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(slots=True)
class Screen:
    """Un écran à afficher : un titre et des lignes de texte.

    Volontairement simple (texte), car l'e-paper est petit et lent : on vise un
    affichage semi-statique, pas une interface riche.
    """

    title: str
    lines: list[str] = field(default_factory=list)


class Display(ABC):
    """Contrat commun à tous les rendus (console, e-paper…)."""

    @abstractmethod
    def show(self, screen: Screen) -> None:
        """Affiche l'écran donné."""
