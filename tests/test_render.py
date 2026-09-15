from PIL import Image

from hestia.display.base import Screen
from hestia.display.png import PngDisplay
from hestia.display.render import DisplaySpec, render_screen

SCREEN = Screen(title="Hestia", lines=["Protection : actif", "Bloquees : 3187"])


def test_render_returns_monochrome_image_of_spec_size():
    spec = DisplaySpec(width=250, height=122)
    image = render_screen(SCREEN, spec)
    assert image.size == (250, 122)
    assert image.mode == "1"  # 1 bit, comme l'e-paper


def test_size_is_configurable():
    image = render_screen(SCREEN, DisplaySpec(width=400, height=300))
    assert image.size == (400, 300)


def test_render_does_not_crash_when_many_lines_overflow():
    spec = DisplaySpec(width=120, height=60)
    screen = Screen(title="T", lines=[f"ligne {i}" for i in range(50)])
    image = render_screen(screen, spec)
    assert image.size == (120, 60)


def test_png_display_writes_file(tmp_path):
    out = tmp_path / "sub" / "screen.png"
    PngDisplay(DisplaySpec(width=200, height=100), out).show(SCREEN)

    assert out.exists()
    with Image.open(out) as reloaded:
        assert reloaded.size == (200, 100)
