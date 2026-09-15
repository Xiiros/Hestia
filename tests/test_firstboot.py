from hestia.display.base import Screen
from hestia.onboarding.firstboot import is_done, mark_done, resolve_dhcp_conflict
from hestia.system.dhcp import DhcpServer

OWN_MAC = "AA:BB:CC:DD:EE:FF"
OWN_IPS = ["192.168.1.50"]
BOX = DhcpServer(server_ip="192.168.1.1", mac="F4:CA:E5:11:22:33")
OURS = DhcpServer(server_ip="192.168.1.50", mac=OWN_MAC)


class FakeDisplay:
    def __init__(self) -> None:
        self.titles: list[str] = []

    def show(self, screen: Screen) -> None:
        self.titles.append(screen.title)

    def clear(self) -> None:
        pass


def _probe_sequence(*rounds):
    """Sonde renvoyant une liste de serveurs différente à chaque appel."""

    calls = iter(rounds)

    def probe(_interface, _timeout):
        return list(next(calls))

    return probe


def test_marker_roundtrip(tmp_path):
    marker = tmp_path / "state" / "first-boot-done"
    assert is_done(marker) is False
    mark_done(marker)
    assert is_done(marker) is True


def test_returns_immediately_when_no_conflict():
    display = FakeDisplay()
    ok = resolve_dhcp_conflict(
        display, _probe_sequence([OURS]), "eth0", OWN_MAC, OWN_IPS, max_attempts=3
    )
    assert ok is True
    assert display.titles == ["Hestia pret"]


def test_loops_until_conflict_resolved():
    display = FakeDisplay()
    slept: list[float] = []
    # Conflit aux deux premières sondes, puis résolu.
    probe = _probe_sequence([BOX], [BOX], [OURS])

    ok = resolve_dhcp_conflict(
        display,
        probe,
        "eth0",
        OWN_MAC,
        OWN_IPS,
        poll_seconds=10.0,
        sleep=slept.append,
    )

    assert ok is True
    # Deux écrans "Action requise" puis l'écran de confirmation.
    assert display.titles == ["Action requise", "Action requise", "Hestia pret"]
    assert slept == [10.0, 10.0]


def test_gives_up_after_max_attempts():
    display = FakeDisplay()
    ok = resolve_dhcp_conflict(
        display,
        _probe_sequence([BOX], [BOX]),
        "eth0",
        OWN_MAC,
        OWN_IPS,
        sleep=lambda _s: None,
        max_attempts=2,
    )
    assert ok is False
    assert display.titles == ["Action requise", "Action requise"]
