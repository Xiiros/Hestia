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

from hestia import __version__
from hestia.adguard import AdGuardClient, AdGuardError, Stats
from hestia.display import Display, build_display
from hestia.display.views import dashboard
from hestia.settings import Settings, load_settings


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="hestia", description="Agent Hestia")
    parser.add_argument("--version", action="version", version=f"hestia {__version__}")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="mode démonstration : écran console et données factices",
    )
    return parser.parse_args(argv)


def _run_demo(display: Display) -> None:
    stats = Stats(num_dns_queries=12045, num_blocked_filtering=3187)
    display.show(dashboard(stats))


def _run(settings: Settings, display: Display) -> None:  # pragma: no cover - boucle
    # Le premier démarrage (détection d'un DHCP concurrent) est branché ici via
    # hestia.onboarding.run_first_boot une fois la sonde réseau disponible.
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


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.demo:
        _run_demo(build_display("console"))
        return 0

    settings = load_settings()
    display = build_display(settings.display.kind)
    _run(settings, display)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
