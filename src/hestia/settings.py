"""Configuration de l'agent.

La config est lue depuis un fichier TOML (par défaut ``/etc/hestia/config.toml``).
Toute valeur absente prend une valeur par défaut raisonnable, pour que l'agent
démarre même sans fichier de configuration.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("/etc/hestia/config.toml")


@dataclass(slots=True)
class AdGuardSettings:
    """Accès à l'API d'AdGuard Home (voir ADR-0003)."""

    base_url: str = "http://127.0.0.1:3000"
    username: str = "admin"
    password: str = ""


@dataclass(slots=True)
class DisplaySettings:
    """Configuration de l'écran."""

    # "console" ou "png" pour le développement, "epaper" sur la Raspberry Pi.
    kind: str = "console"
    refresh_seconds: int = 30
    # Géométrie (indépendante du pilote) — à ajuster selon le modèle d'écran.
    width: int = 250
    height: int = 122
    font_path: str = ""  # TTF optionnel ; sinon police par défaut
    # Modèle de pilote Waveshare (pour kind="epaper").
    model: str = "epd2in13_V4"
    # Fichier de sortie pour kind="png".
    png_path: str = "hestia-screen.png"


@dataclass(slots=True)
class UpdateSettings:
    """Mises à jour OTA (voir ADR-0005)."""

    channel: str = "stable"  # "stable" ou "beta"
    check_seconds: int = 3600
    repo: str = "Xiiros/Hestia"  # dépôt interrogé via l'API GitHub (owner/nom)
    install_root: str = "/opt/hestia"  # contient releases/ et le lien current
    public_key_path: str = "/etc/hestia/update-key.pub"  # clé publique Ed25519 (PEM)
    asset_suffix: str = ".tar.gz"  # suffixe de l'artefact de mise à jour


@dataclass(slots=True)
class NetworkSettings:
    """Paramètres réseau utilisés par la sonde DHCP."""

    interface: str = "eth0"
    dhcp_probe_timeout: float = 5.0
    first_boot_poll_seconds: float = 15.0  # intervalle de re-sonde en cas de conflit


@dataclass(slots=True)
class DhcpSettings:
    """Serveur DHCP d'AdGuard Home activé par Hestia à la fin du premier démarrage.

    Désactivé par défaut : tant que la plage n'est pas renseignée, on n'active
    rien (un DHCP mal configuré casserait le réseau du foyer).
    """

    enable_on_first_boot: bool = False
    interface: str = "eth0"
    gateway_ip: str = ""  # IP de la box (passerelle Internet des clients)
    subnet_mask: str = "255.255.255.0"
    range_start: str = ""
    range_end: str = ""
    lease_duration: int = 86400


@dataclass(slots=True)
class Settings:
    adguard: AdGuardSettings = field(default_factory=AdGuardSettings)
    display: DisplaySettings = field(default_factory=DisplaySettings)
    update: UpdateSettings = field(default_factory=UpdateSettings)
    network: NetworkSettings = field(default_factory=NetworkSettings)
    dhcp: DhcpSettings = field(default_factory=DhcpSettings)
    # Données d'état persistantes (marqueur de premier démarrage, etc.).
    state_dir: str = "/var/lib/hestia"


def load_settings(path: Path | None = None) -> Settings:
    """Charge la configuration ; renvoie les valeurs par défaut si le fichier
    est absent."""

    path = path or DEFAULT_CONFIG_PATH
    if not path.exists():
        return Settings()

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    settings = Settings(
        adguard=AdGuardSettings(**data.get("adguard", {})),
        display=DisplaySettings(**data.get("display", {})),
        update=UpdateSettings(**data.get("update", {})),
        network=NetworkSettings(**data.get("network", {})),
        dhcp=DhcpSettings(**data.get("dhcp", {})),
    )
    if "state_dir" in data:
        settings.state_dir = data["state_dir"]
    return settings
