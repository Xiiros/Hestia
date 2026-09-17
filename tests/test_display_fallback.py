import pytest

from hestia.display import choose_display
from hestia.display.base import Display, Screen


class DummyDisplay(Display):
    def __init__(self, name: str) -> None:
        self.name = name

    def show(self, screen: Screen) -> None:
        pass


def _ok(name: str):
    return lambda: DummyDisplay(name)


def _fail(exc: Exception):
    def factory():
        raise exc

    return factory


def test_returns_first_available():
    display = choose_display([("epaper", _ok("epaper")), ("console", _ok("console"))])
    assert isinstance(display, DummyDisplay)
    assert display.name == "epaper"


def test_falls_back_when_first_fails():
    display = choose_display(
        [
            ("epaper", _fail(RuntimeError("pas de panneau"))),
            ("window", _ok("window")),
            ("console", _ok("console")),
        ]
    )
    assert display.name == "window"


def test_falls_back_to_last_when_all_others_fail():
    display = choose_display(
        [
            ("epaper", _fail(RuntimeError("pas de panneau"))),
            ("window", _fail(RuntimeError("pas d'affichage"))),
            ("console", _ok("console")),
        ]
    )
    assert display.name == "console"


def test_raises_last_error_when_all_fail():
    boom = RuntimeError("rien ne marche")
    with pytest.raises(RuntimeError, match="rien ne marche"):
        choose_display([("a", _fail(RuntimeError("x"))), ("b", _fail(boom))])
