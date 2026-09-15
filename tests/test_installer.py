from pathlib import Path

from hestia.updater.installer import Installer, InstallPaths, current_version


def _extractor(marker: str):
    """Extracteur factice : écrit un fichier marqueur dans le dossier cible."""

    def extract(artifact: bytes, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "content.txt").write_bytes(artifact + marker.encode())

    return extract


def test_current_version_is_none_before_any_install(tmp_path):
    assert current_version(InstallPaths(tmp_path)) is None


def test_apply_activates_healthy_release(tmp_path):
    paths = InstallPaths(tmp_path)
    installer = Installer(paths, extractor=_extractor("v1"), health_check=lambda _d: True)

    assert installer.apply("1.0.0", b"data") is True
    assert current_version(paths) == "1.0.0"
    assert (paths.release_dir("1.0.0") / "content.txt").exists()


def test_failed_health_check_rolls_back_to_previous(tmp_path):
    paths = InstallPaths(tmp_path)
    healthy = Installer(paths, extractor=_extractor("v1"), health_check=lambda _d: True)
    healthy.apply("1.0.0", b"data")

    broken = Installer(paths, extractor=_extractor("v2"), health_check=lambda _d: False)
    assert broken.apply("1.1.0", b"data") is False
    # On est revenu à la version précédente, saine.
    assert current_version(paths) == "1.0.0"


def test_failed_first_install_has_no_previous(tmp_path):
    paths = InstallPaths(tmp_path)
    installer = Installer(paths, extractor=_extractor("v1"), health_check=lambda _d: False)
    assert installer.apply("1.0.0", b"data") is False
    # Pas de version précédente : le lien pointe encore sur l'échec (à nettoyer
    # au prochain cycle), mais aucune version saine n'existait.
    assert current_version(paths) == "1.0.0"
