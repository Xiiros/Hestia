from hestia.updater.versions import is_newer, parse


def test_parse_ignores_prefix_and_suffix():
    assert parse("v1.4.2-beta.1") == (1, 4, 2)
    assert parse("1.4.2+build.7") == (1, 4, 2)


def test_is_newer():
    assert is_newer("1.3.0", "1.2.0") is True
    assert is_newer("1.3.0", "1.3.0") is False
    assert is_newer("1.2.9", "1.3.0") is False


def test_is_newer_ignores_tags_and_prerelease_suffix():
    assert is_newer("v1.2.1-beta.1", "v1.2.0") is True
