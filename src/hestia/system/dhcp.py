"""Détection d'un serveur DHCP concurrent sur le réseau local.

Principe : on envoie une requête DHCP DISCOVER en broadcast et on écoute les
DHCP OFFER. Chaque OFFER révèle un serveur DHCP actif (typiquement la box du
foyer). Si un serveur autre que nous répond, il faut désactiver le DHCP de la
box avant qu'Hestia ne prenne le relais (voir le flux d'onboarding).

La partie « entrées/sorties réseau » (``probe_dhcp_servers``) s'appuie sur
scapy et nécessite les privilèges root ; elle est isolée de la logique pure
(``is_foreign``) pour rester testable sans matériel ni privilèges.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DhcpServer:
    """Un serveur DHCP ayant répondu à notre DISCOVER."""

    server_ip: str  # adresse du serveur (souvent la passerelle)
    mac: str  # MAC source de la réponse
    offered_ip: str = ""  # adresse proposée au client
    hostname: str = ""  # nom éventuel annoncé par le serveur


def is_foreign(server: DhcpServer, own_mac: str, own_ips: Iterable[str]) -> bool:
    """Vrai si ``server`` est un DHCP tiers (ni notre MAC, ni nos IP)."""

    from hestia.system.vendors import normalize_mac

    if normalize_mac(server.mac) == normalize_mac(own_mac):
        return False
    return server.server_ip not in set(own_ips)


def find_foreign_servers(
    servers: Iterable[DhcpServer], own_mac: str, own_ips: Iterable[str]
) -> list[DhcpServer]:
    """Filtre la liste des serveurs pour ne garder que les DHCP concurrents."""

    own_ips = list(own_ips)
    return [s for s in servers if is_foreign(s, own_mac, own_ips)]


def probe_dhcp_servers(interface: str, timeout: float = 5.0) -> list[DhcpServer]:
    """Envoie un DHCP DISCOVER et renvoie les serveurs ayant répondu.

    Nécessite scapy (extra « net ») et les privilèges root. Import tardif pour ne
    pas imposer scapy à tout le paquet.
    """

    try:
        from scapy.all import (  # type: ignore[import-untyped]
            BOOTP,
            DHCP,
            IP,
            UDP,
            Ether,
            get_if_hwaddr,
            srp,
        )
    except ImportError as exc:  # pragma: no cover - dépend de l'extra « net »
        raise RuntimeError(
            "scapy est requis pour sonder le DHCP : installez l'extra « net » "
            "(uv sync --extra net) et lancez l'agent en root."
        ) from exc

    hw = get_if_hwaddr(interface)
    discover = (
        Ether(src=hw, dst="ff:ff:ff:ff:ff:ff")
        / IP(src="0.0.0.0", dst="255.255.255.255")
        / UDP(sport=68, dport=67)
        / BOOTP(chaddr=_mac_to_bytes(hw))
        / DHCP(options=[("message-type", "discover"), "end"])
    )
    answered, _ = srp(discover, iface=interface, timeout=timeout, verbose=False)

    servers: list[DhcpServer] = []
    for _sent, received in answered:
        servers.append(_server_from_offer(received))
    return servers


def _mac_to_bytes(mac: str) -> bytes:
    return bytes(int(part, 16) for part in mac.split(":"))


def _server_from_offer(packet) -> DhcpServer:  # pragma: no cover - dépend de scapy
    """Extrait un ``DhcpServer`` d'un paquet DHCP OFFER scapy."""

    options = dict(
        opt[:2] if isinstance(opt, tuple) and len(opt) >= 2 else (opt, None)
        for opt in packet["DHCP"].options
        if isinstance(opt, tuple)
    )
    server_ip = options.get("server_id") or packet["IP"].src
    return DhcpServer(
        server_ip=str(server_ip),
        mac=packet["Ether"].src,
        offered_ip=str(packet["BOOTP"].yiaddr),
        hostname=str(options.get("hostname", "")),
    )
