from hestia.updater.sources import select_release

SUFFIX = ".tar.gz"


def _asset(name: str) -> dict:
    return {"name": name, "browser_download_url": f"https://dl/{name}"}


def _release(tag: str, *, prerelease: bool, with_sig: bool = True, draft: bool = False) -> dict:
    assets = [_asset(f"hestia-{tag}{SUFFIX}")]
    if with_sig:
        assets.append(_asset(f"hestia-{tag}{SUFFIX}.sig"))
    return {"tag_name": tag, "prerelease": prerelease, "draft": draft, "assets": assets}


def test_stable_skips_prereleases():
    releases = [
        _release("v1.3.0-beta.1", prerelease=True),
        _release("v1.2.0", prerelease=False),
    ]
    result = select_release(releases, "stable", SUFFIX)
    assert result is not None
    assert result.version == "1.2.0"
    assert result.prerelease is False
    assert result.artifact_url == "https://dl/hestia-v1.2.0.tar.gz"
    assert result.signature_url == "https://dl/hestia-v1.2.0.tar.gz.sig"


def test_beta_takes_prerelease_when_most_recent():
    releases = [
        _release("v1.3.0-beta.1", prerelease=True),
        _release("v1.2.0", prerelease=False),
    ]
    assert select_release(releases, "beta", SUFFIX).version == "1.3.0-beta.1".lstrip("v")


def test_release_without_signature_is_skipped():
    releases = [
        _release("v1.3.0", prerelease=False, with_sig=False),
        _release("v1.2.0", prerelease=False),
    ]
    assert select_release(releases, "stable", SUFFIX).version == "1.2.0"


def test_draft_is_skipped():
    releases = [_release("v1.3.0", prerelease=False, draft=True)]
    assert select_release(releases, "stable", SUFFIX) is None


def test_no_release_returns_none():
    assert select_release([], "stable", SUFFIX) is None
