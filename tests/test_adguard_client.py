import json

import httpx
import pytest

from hestia.adguard import AdGuardClient, AdGuardError, DhcpConfig


class FakeAdGuard:
    """Transport HTTP simulant AdGuard Home (aucun réseau)."""

    def __init__(self, routes: dict[str, tuple[int, dict]]):
        self.routes = routes
        self.requests: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        status, body = self.routes.get(request.url.path, (404, {}))
        return httpx.Response(status, json=body)

    def paths(self) -> list[str]:
        return [r.url.path for r in self.requests]


def _client(fake: FakeAdGuard, *, username: str = "admin") -> AdGuardClient:
    http = httpx.Client(base_url="http://agh", transport=httpx.MockTransport(fake.handler))
    return AdGuardClient("http://agh", username, "secret", client=http)


def test_login_then_get_stats():
    fake = FakeAdGuard(
        {
            "/control/login": (200, {}),
            "/control/stats": (200, {"num_dns_queries": 100, "num_blocked_filtering": 40}),
        }
    )
    stats = _client(fake).get_stats()

    assert stats.num_dns_queries == 100
    assert stats.blocked_percentage == 40.0
    assert fake.paths() == ["/control/login", "/control/stats"]  # connexion d'abord


def test_no_auth_instance_skips_login():
    fake = FakeAdGuard({"/control/status": (200, {"protection_enabled": True})})
    assert _client(fake, username="").is_protection_enabled() is True
    assert fake.paths() == ["/control/status"]  # pas de /control/login


def test_configure_dhcp_posts_expected_body():
    fake = FakeAdGuard({"/control/login": (200, {}), "/control/dhcp/set_config": (200, {})})
    config = DhcpConfig(
        interface="eth0",
        gateway_ip="192.168.1.1",
        subnet_mask="255.255.255.0",
        range_start="192.168.1.100",
        range_end="192.168.1.200",
    )
    _client(fake).configure_dhcp(config)

    post = fake.requests[-1]
    assert post.method == "POST"
    assert post.url.path == "/control/dhcp/set_config"
    assert json.loads(post.content) == config.to_api()


def test_http_error_is_wrapped():
    fake = FakeAdGuard({"/control/login": (200, {}), "/control/stats": (500, {})})
    with pytest.raises(AdGuardError):
        _client(fake).get_stats()


def test_login_failure_is_wrapped():
    fake = FakeAdGuard({"/control/login": (403, {})})
    with pytest.raises(AdGuardError):
        _client(fake).get_status()
