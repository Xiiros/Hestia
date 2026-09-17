from hestia.app import _parse_args


def test_defaults():
    args = _parse_args([])
    assert args.demo is False
    assert args.png is None
    assert args.window is False


def test_demo_window_flag():
    args = _parse_args(["--demo", "--window"])
    assert args.demo is True
    assert args.window is True


def test_demo_png_flag():
    args = _parse_args(["--demo", "--png", "out.png"])
    assert args.png == "out.png"
