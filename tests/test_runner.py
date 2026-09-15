from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from hestia.updater.models import Release, UpdateStatus
from hestia.updater.runner import UpdateRunner

ARTIFACT_URL = "https://dl/hestia.tar.gz"
SIG_URL = "https://dl/hestia.tar.gz.sig"
ARTIFACT = b"contenu de la mise a jour"


def _keypair():
    private = Ed25519PrivateKey.generate()
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private, public_pem


class FakeSource:
    def __init__(self, release: Release | None):
        self._release = release

    def latest(self, _channel: str) -> Release | None:
        return self._release


class FakeInstaller:
    def __init__(self, ok: bool = True):
        self.ok = ok
        self.applied: list[str] = []

    def apply(self, version: str, artifact: bytes) -> bool:
        self.applied.append(version)
        return self.ok


def _release(version="1.3.0", prerelease=False):
    return Release(
        version=version,
        tag=f"v{version}",
        prerelease=prerelease,
        artifact_url=ARTIFACT_URL,
        signature_url=SIG_URL,
    )


def _downloader(private):
    signature = private.sign(ARTIFACT)
    mapping = {ARTIFACT_URL: ARTIFACT, SIG_URL: signature}

    def download(url: str) -> bytes:
        return mapping[url]

    return download


def test_no_release_available():
    private, public_pem = _keypair()
    runner = UpdateRunner(FakeSource(None), FakeInstaller(), public_pem, _downloader(private))
    assert runner.run_once("1.0.0").status == UpdateStatus.NO_RELEASE


def test_up_to_date():
    private, public_pem = _keypair()
    runner = UpdateRunner(
        FakeSource(_release("1.0.0")), FakeInstaller(), public_pem, _downloader(private)
    )
    assert runner.run_once("1.0.0").status == UpdateStatus.UP_TO_DATE


def test_applied_when_signature_valid_and_healthy():
    private, public_pem = _keypair()
    installer = FakeInstaller(ok=True)
    runner = UpdateRunner(FakeSource(_release()), installer, public_pem, _downloader(private))
    result = runner.run_once("1.0.0")
    assert result.status == UpdateStatus.APPLIED
    assert result.to_version == "1.3.0"
    assert installer.applied == ["1.3.0"]


def test_rolled_back_when_health_check_fails():
    private, public_pem = _keypair()
    runner = UpdateRunner(
        FakeSource(_release()), FakeInstaller(ok=False), public_pem, _downloader(private)
    )
    assert runner.run_once("1.0.0").status == UpdateStatus.ROLLED_BACK


def test_bad_signature_is_refused_and_not_installed():
    _, public_pem = _keypair()
    attacker, _ = _keypair()
    installer = FakeInstaller()
    runner = UpdateRunner(FakeSource(_release()), installer, public_pem, _downloader(attacker))
    result = runner.run_once("1.0.0")
    assert result.status == UpdateStatus.BAD_SIGNATURE
    assert installer.applied == []  # rien n'est installé sans signature valide
