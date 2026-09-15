from hestia.system.dhcp import DhcpServer, find_foreign_servers, is_foreign

OWN_MAC = "AA:BB:CC:DD:EE:FF"
OWN_IPS = ["192.168.1.50"]


def _server(ip: str, mac: str) -> DhcpServer:
    return DhcpServer(server_ip=ip, mac=mac, offered_ip="192.168.1.100")


def test_foreign_server_is_detected():
    box = _server("192.168.1.1", "F4:CA:E5:11:22:33")
    assert is_foreign(box, OWN_MAC, OWN_IPS) is True


def test_our_own_server_is_not_foreign_by_mac():
    ours = _server("192.168.1.1", OWN_MAC.lower())
    assert is_foreign(ours, OWN_MAC, OWN_IPS) is False


def test_our_own_server_is_not_foreign_by_ip():
    ours = _server("192.168.1.50", "F4:CA:E5:11:22:33")
    assert is_foreign(ours, OWN_MAC, OWN_IPS) is False


def test_find_foreign_servers_filters_ours():
    servers = [
        _server("192.168.1.1", "F4:CA:E5:11:22:33"),
        _server("192.168.1.50", OWN_MAC),
    ]
    foreign = find_foreign_servers(servers, OWN_MAC, OWN_IPS)
    assert len(foreign) == 1
    assert foreign[0].server_ip == "192.168.1.1"
