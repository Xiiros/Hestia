"""Point d'entrée de l'agent Hestia.

Orchestration : premier démarrage (détection DHCP), puis boucle d'affichage du
tableau de bord alimentée par l'API d'AdGuard Home.

Utilisation :
    hestia                 # exécution normale
    hestia --demo          # démonstration sans matériel ni AdGuard Home
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from hestia import __version__
from hestia.adguard import AdGuardClient, AdGuardError, Stats
from hestia.display import Display, build_display
from hestia.display.views import dashboard
from hestia.onboarding import firstboot
from hestia.settings import Settings, load_settings
from hestia.system import probe_dhcp_servers, read_ipv4_addresses, read_mac


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="hestia", description="Agent Hestia")
    parser.add_argument("--version", action="version", version=f"hestia {__version__}")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="mode démonstration : données factices, sans matériel ni AdGuard Home",
    )
    parser.add_argument(
        "--png",
        metavar="FICHIER",
        help="en démo : rend l'écran dans ce fichier PNG au lieu du terminal",
    )
    return parser.parse_args(argv)


def _run_demo(display: Display) -> None:
    stats = Stats(num_dns_queries=12045, num_blocked_filtering=3187)
    display.show(dashboard(stats))


def _first_boot(settings: Settings, display: Display) -> None:  # pragma: no cover - I/O
    """Détecte et fait résoudre un conflit DHCP au tout premier démarrage."""

    marker = Path(settings.state_dir) / "first-boot-done"
    if firstboot.is_done(marker):
        return

    interface = settings.network.interface
    resolved = firstboot.resolve_dhcp_conflict(
        display,
        probe_dhcp_servers,
        interface,
        read_mac(interface),
        read_ipv4_addresses(interface),
        poll_seconds=settings.network.first_boot_poll_seconds,
        timeout=settings.network.dhcp_probe_timeout,
    )
    if resolved:
        # TODO: activer le serveur DHCP d'AdGuard Home ici (via son API) avant
        # de marquer le premier démarrage comme terminé.
        firstboot.mark_done(marker)


def _run(settings: Settings, display: Display) -> None:  # pragma: no cover - boucle
    _first_boot(settings, display)
    with AdGuardClient(
        settings.adguard.base_url,
        settings.adguard.username,
        settings.adguard.password,
    ) as client:
        while True:
            try:
                stats = client.get_stats()
                protection_on = client.is_protection_enabled()
                display.show(dashboard(stats, protection_on=protection_on))
            except AdGuardError as exc:
                print(f"[hestia] AdGuard indisponible : {exc}")
            time.sleep(settings.display.refresh_seconds)


def _demo_display(png_path: str | None) -> Display:
    if png_path:
        from hestia.display.png import PngDisplay
        from hestia.display.render import DisplaySpec

        return PngDisplay(DisplaySpec(), Path(png_path))
    from hestia.display import ConsoleDisplay

    return ConsoleDisplay()


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.demo:
        display = _demo_display(args.png)
        _run_demo(display)
        if args.png:
            print(f"[hestia] écran rendu dans {args.png}")
        return 0

    settings = load_settings()
    display = build_display(settings.display)
    _run(settings, display)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
