import pytest

from app.utils.url_to_norm import normalize_stepik_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://stepik.org/users/12345", "https://stepik.org/users/12345"),
        ("https://stepik.org/users/12345/", "https://stepik.org/users/12345"),
        (
            "https://stepik.org/users/12345/profile/",
            "https://stepik.org/users/12345",
        ),
        (
            "https://stepik.org/users/12345/profile/?query=1",
            "https://stepik.org/users/12345",
        ),
    ],
)
def test_normalize_stepik_url_valid_cases(url: str, expected: str) -> None:
    assert normalize_stepik_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "",
        "https://example.com/users/1",
        "https://stepik.org/users/not-a-number",
        "ftp://stepik.org/users/12345",
    ],
)
def test_normalize_stepik_url_invalid_cases(url: str) -> None:
    assert normalize_stepik_url(url) is None
