from hestia.updater import check_for_update


def test_update_available_when_latest_is_greater():
    info = check_for_update("1.2.0", "1.3.0")
    assert info.update_available is True


def test_no_update_when_equal():
    assert check_for_update("1.3.0", "1.3.0").update_available is False


def test_no_update_when_current_is_greater():
    assert check_for_update("1.3.1", "1.3.0").update_available is False


def test_tags_and_suffixes_are_ignored():
    assert check_for_update("v1.2.0", "v1.2.1-beta.1").update_available is True
