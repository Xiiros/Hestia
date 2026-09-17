"""Afficheur fenêtre bureau (repli quand l'e-paper n'est pas détecté).

Affiche le même rendu (image PIL) dans une fenêtre Tkinter sur le bureau de la
Raspberry Pi. Utile pour tester ou dépanner sans écran e-paper branché.

Nécessite un environnement graphique (serveur X) et ``python3-tk``. Si l'un manque,
la construction échoue — la fabrique retombe alors sur la console.
"""

from __future__ import annotations

from hestia.display.base import Display, Screen
from hestia.display.render import DisplaySpec, render_screen


class WindowDisplay(Display):
    def __init__(self, spec: DisplaySpec, *, scale: int = 3, title: str = "Hestia") -> None:
        import tkinter as tk  # peut lever ImportError (python3-tk absent)

        self._spec = spec
        self._scale = max(1, scale)
        self._root = tk.Tk()  # peut lever TclError (pas d'affichage graphique)
        self._root.title(title)
        self._label = tk.Label(self._root)
        self._label.pack()
        self._photo = None  # garde une référence (sinon l'image est ramassée)
        self._root.update()

    def show(self, screen: Screen) -> None:  # pragma: no cover - dépend de l'affichage
        from PIL import ImageTk

        image = render_screen(screen, self._spec).convert("L")
        if self._scale != 1:
            image = image.resize((self._spec.width * self._scale, self._spec.height * self._scale))
        self._photo = ImageTk.PhotoImage(image)
        self._label.configure(image=self._photo)
        self._root.update_idletasks()
        self._root.update()

    def clear(self) -> None:  # pragma: no cover - dépend de l'affichage
        self._label.configure(image="")
        self._root.update()
