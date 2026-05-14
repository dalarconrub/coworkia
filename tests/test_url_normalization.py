from tools.url_normalization import canonical_url


def test_canonical_url_removes_tracking_and_fragment():
    assert canonical_url(
        "HTTPS://Example.com/Post/?utm_source=news&utm_medium=email&id=7#section"
    ) == "https://example.com/Post?id=7"


def test_canonical_url_removes_trailing_slash_except_root():
    assert canonical_url("https://example.com/post/") == "https://example.com/post"
    assert canonical_url("https://example.com/") == "https://example.com/"


def test_canonical_url_sorts_remaining_query_params():
    assert canonical_url("https://example.com?a=2&b=1&utm_campaign=x") == "https://example.com?a=2&b=1"
