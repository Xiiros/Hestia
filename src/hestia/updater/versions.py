"""Comparaison de versions SemVer."""

from __future__ import annotations


def parse(version: str) -> tuple[int, int, int]:
    """« v1.4.2-beta.1 » -> (1, 4, 2). Ignore le préfixe « v » et les suffixes."""

    core = version.lstrip("vV").split("+")[0].split("-")[0]
    major, minor, patch, *_ = (*core.split("."), "0", "0", "0")
    return int(major), int(minor), int(patch)


def is_newer(candidate: str, current: str) -> bool:
    """Vrai si ``candidate`` est une version strictement plus récente."""

    return parse(candidate) > parse(current)
