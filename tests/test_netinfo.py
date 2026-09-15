import pytest

from hestia.system.netinfo import read_mac


def test_read_mac_from_sysfs(tmp_path):
    iface_dir = tmp_path / "eth0"
    iface_dir.mkdir()
    (iface_dir / "address").write_text("aa:bb:cc:dd:ee:ff\n")

    assert read_mac("eth0", sysfs_root=tmp_path) == "aa:bb:cc:dd:ee:ff"


def test_read_mac_missing_interface_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_mac("does-not-exist", sysfs_root=tmp_path)
