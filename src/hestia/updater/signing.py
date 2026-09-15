"""Vérification de signature des artefacts de mise à jour.

Chaque artefact est accompagné d'une **signature détachée Ed25519**. L'appareil
n'embarque que la **clé publique** ; la clé privée reste hors des boîtiers (dans
les secrets CI). Un appareil n'installe donc que ce qui est authentiquement signé
par l'équipe (voir ADR-0005).

``cryptography`` est importé tardivement (extra « ota ») pour ne pas l'imposer à
tout le paquet.
"""

from __future__ import annotations

from pathlib import Path


def load_public_key(path: str | Path) -> bytes:
    """Lit la clé publique (format PEM) depuis le disque."""

    return Path(path).read_bytes()


def verify_signature(data: bytes, signature: bytes, public_key_pem: bytes) -> bool:
    """Vrai si ``signature`` est une signature Ed25519 valide de ``data``."""

    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
    except ImportError as exc:  # pragma: no cover - dépend de l'extra « ota »
        raise RuntimeError(
            "cryptography est requis pour vérifier les signatures : installez "
            "l'extra « ota » (uv sync --extra ota)."
        ) from exc

    key = load_pem_public_key(public_key_pem)
    try:
        key.verify(signature, data)  # Ed25519 : lève si invalide
    except InvalidSignature:
        return False
    return True
