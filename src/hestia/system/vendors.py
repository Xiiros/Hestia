"""Identification du fournisseur d'accès (box) à partir de l'adresse MAC.

La correspondance OUI (3 premiers octets de la MAC) → fabricant est **une
estimation** : les FAI utilisent divers fabricants et changent de matériel. On
s'en sert uniquement pour proposer un tutoriel plus précis ; en cas de doute, le
tutoriel générique reste toujours disponible.

La table est volontairement courte et facile à enrichir (au besoin depuis la
base OUI de l'IEEE).
"""

from __future__ import annotations

from enum import StrEnum


class Isp(StrEnum):
    ORANGE = "orange"  # Livebox
    FREE = "free"  # Freebox
    BOUYGUES = "bouygues"  # Bbox
    SFR = "sfr"  # SFR Box
    UNKNOWN = "unknown"


# Préfixes OUI (majuscules, séparés par « : ») → FAI présumé.
# À compléter avec de vraies observations terrain.
_OUI_TO_ISP: dict[str, Isp] = {
    "44:A6:1E": Isp.FREE,  # Freebox Delta/Pop (exemple)
    "F4:CA:E5": Isp.FREE,
    "00:07:CB": Isp.ORANGE,  # Sagemcom (Livebox)
    "A0:1B:29": Isp.ORANGE,
    "E4:5D:51": Isp.BOUYGUES,  # Bbox
    "34:DB:9C": Isp.SFR,  # SFR Box
}


def normalize_mac(mac: str) -> str:
    """Renvoie la MAC en majuscules avec « : » comme séparateur."""

    cleaned = mac.strip().upper().replace("-", ":")
    return cleaned


def oui_of(mac: str) -> str:
    """Renvoie l'OUI (3 premiers octets) d'une adresse MAC."""

    return ":".join(normalize_mac(mac).split(":")[:3])


def guess_isp(mac: str | None) -> Isp:
    """Devine le FAI depuis la MAC de la box. ``Isp.UNKNOWN`` si non reconnu."""

    if not mac:
        return Isp.UNKNOWN
    return _OUI_TO_ISP.get(oui_of(mac), Isp.UNKNOWN)
