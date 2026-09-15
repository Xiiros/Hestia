from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from hestia.updater.signing import verify_signature


def _keypair() -> tuple[Ed25519PrivateKey, bytes]:
    private = Ed25519PrivateKey.generate()
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private, public_pem


def test_valid_signature_is_accepted():
    private, public_pem = _keypair()
    data = b"artefact de mise a jour"
    assert verify_signature(data, private.sign(data), public_pem) is True


def test_tampered_data_is_rejected():
    private, public_pem = _keypair()
    signature = private.sign(b"contenu original")
    assert verify_signature(b"contenu modifie", signature, public_pem) is False


def test_signature_from_other_key_is_rejected():
    attacker, _ = _keypair()
    _, public_pem = _keypair()
    data = b"artefact"
    assert verify_signature(data, attacker.sign(data), public_pem) is False
