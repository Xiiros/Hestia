from hestia.display.base import Screen
from hestia.onboarding.flow import check_dhcp_conflict, run_first_boot
from hestia.onboarding.tutorials import generic_tutorial, tutorial_for
from hestia.system.dhcp import DhcpServer
from hestia.system.vendors import Isp

OWN_MAC = "AA:BB:CC:DD:EE:FF"
OWN_IPS = ["192.168.1.50"]


class FakeDisplay:
    def __init__(self) -> None:
        self.shown: list[Screen] = []

    def show(self, screen: Screen) -> None:
        self.shown.append(screen)

    def clear(self) -> None:
        pass


def _probe_with(servers):
    def probe(_interface, _timeout):
        return list(servers)

    return probe


def test_no_conflict_when_only_our_server_answers():
    probe = _probe_with([DhcpServer(server_ip="192.168.1.50", mac=OWN_MAC)])
    result = check_dhcp_conflict(probe, "eth0", OWN_MAC, OWN_IPS)
    assert result.conflict is False


def test_conflict_selects_tutorial_for_known_box():
    box = DhcpServer(server_ip="192.168.1.1", mac="F4:CA:E5:11:22:33")
    result = check_dhcp_conflict(_probe_with([box]), "eth0", OWN_MAC, OWN_IPS)
    assert result.conflict is True
    assert result.tutorial == tutorial_for(Isp.FREE, "http://192.168.1.1")


def test_unknown_box_falls_back_to_generic_with_gateway_url():
    box = DhcpServer(server_ip="10.0.0.1", mac="11:22:33:44:55:66")
    result = check_dhcp_conflict(_probe_with([box]), "eth0", OWN_MAC, OWN_IPS)
    assert result.tutorial == generic_tutorial("http://10.0.0.1")
    assert "http://10.0.0.1" in result.tutorial.steps[0]


def test_run_first_boot_shows_screen_on_conflict():
    box = DhcpServer(server_ip="192.168.1.1", mac="F4:CA:E5:11:22:33")
    display = FakeDisplay()
    run_first_boot(display, _probe_with([box]), "eth0", OWN_MAC, OWN_IPS)
    assert len(display.shown) == 1
    assert "192.168.1.1" in " ".join(display.shown[0].lines)
