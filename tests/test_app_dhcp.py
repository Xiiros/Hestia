from hestia.app import build_dhcp_config
from hestia.settings import DhcpSettings


def test_no_config_when_disabled():
    dhcp = DhcpSettings(
        enable_on_first_boot=False,
        gateway_ip="192.168.1.1",
        range_start="192.168.1.100",
        range_end="192.168.1.200",
    )
    assert build_dhcp_config(dhcp) is None


def test_no_config_when_range_missing():
    dhcp = DhcpSettings(enable_on_first_boot=True, gateway_ip="192.168.1.1")
    assert build_dhcp_config(dhcp) is None


def test_config_built_when_enabled_and_complete():
    dhcp = DhcpSettings(
        enable_on_first_boot=True,
        interface="eth0",
        gateway_ip="192.168.1.1",
        range_start="192.168.1.100",
        range_end="192.168.1.200",
    )
    config = build_dhcp_config(dhcp)
    assert config is not None
    assert config.gateway_ip == "192.168.1.1"
    assert config.to_api()["enabled"] is True
