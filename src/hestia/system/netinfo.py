"""Lecture des informations réseau locales de l'appareil.

Sert à alimenter la sonde DHCP : pour reconnaître notre propre serveur, il faut
connaître notre MAC et nos adresses IP.
"""

from __future__ import annotations

from pathlib import Path

_SYSFS_NET = Path("/sys/class/net")


def read_mac(interface: str, sysfs_root: Path = _SYSFS_NET) -> str:
    """Lit l'adresse MAC de l'interface (via ``/sys/class/net``)."""

    return (sysfs_root / interface / "address").read_text().strip()


def read_ipv4_addresses(interface: str) -> list[str]:
    """Renvoie les IPv4 de l'interface (liste vide si aucune / erreur).

    Best-effort via ioctl SIOCGIFADDR (Linux). Une interface sans IP au premier
    démarrage renvoie simplement une liste vide.
    """

    try:  # pragma: no cover - dépend de l'interface réseau réelle
        import fcntl
        import socket
        import struct

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packed = struct.pack("256s", interface[:15].encode())
        addr = fcntl.ioctl(sock.fileno(), 0x8915, packed)[20:24]  # SIOCGIFADDR
        return [socket.inet_ntoa(addr)]
    except OSError:
        return []
