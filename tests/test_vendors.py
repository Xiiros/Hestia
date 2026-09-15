from hestia.system.vendors import Isp, guess_isp, normalize_mac, oui_of


def test_normalize_mac_uppercases_and_uses_colons():
    assert normalize_mac("f4-ca-e5-11-22-33") == "F4:CA:E5:11:22:33"


def test_oui_of_keeps_first_three_octets():
    assert oui_of("f4:ca:e5:11:22:33") == "F4:CA:E5"


def test_guess_isp_recognizes_known_prefix():
    assert guess_isp("F4:CA:E5:11:22:33") == Isp.FREE


def test_guess_isp_unknown_prefix():
    assert guess_isp("11:22:33:44:55:66") == Isp.UNKNOWN


def test_guess_isp_handles_none():
    assert guess_isp(None) == Isp.UNKNOWN
