from hestia.adguard.models import DhcpConfig, DhcpStatus, Stats, Status


def test_stats_blocked_percentage():
    stats = Stats.from_api({"num_dns_queries": 200, "num_blocked_filtering": 50})
    assert stats.blocked_percentage == 25.0


def test_stats_percentage_is_zero_without_queries():
    assert Stats(0, 0).blocked_percentage == 0.0


def test_status_from_api():
    status = Status.from_api({"running": True, "protection_enabled": True, "version": "v0.107.0"})
    assert status.running is True
    assert status.protection_enabled is True
    assert status.version == "v0.107.0"


def test_dhcp_status_from_api():
    dhcp = DhcpStatus.from_api({"enabled": True, "interface_name": "eth0"})
    assert dhcp.enabled is True
    assert dhcp.interface == "eth0"


def test_dhcp_config_to_api_schema():
    config = DhcpConfig(
        interface="eth0",
        gateway_ip="192.168.1.1",
        subnet_mask="255.255.255.0",
        range_start="192.168.1.100",
        range_end="192.168.1.200",
        lease_duration=3600,
    )
    payload = config.to_api()
    assert payload["enabled"] is True
    assert payload["interface_name"] == "eth0"
    assert payload["v4"] == {
        "gateway_ip": "192.168.1.1",
        "subnet_mask": "255.255.255.0",
        "range_start": "192.168.1.100",
        "range_end": "192.168.1.200",
        "lease_duration": 3600,
    }
