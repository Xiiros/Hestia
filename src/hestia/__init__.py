"""Agent Hestia : surcouche AdGuard Home, écran e-paper et mises à jour."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("hestia")
except PackageNotFoundError:  # exécution depuis les sources non installées
    __version__ = "0.0.0+dev"

__all__ = ["__version__"]
