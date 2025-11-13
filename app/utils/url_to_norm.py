
"""Хелперы для ссылок Stepik."""


def normalize_stepik_url(url: str) -> str | None:
    """Возвращает https://stepik.org/users/<id> или None,
    если ссылка некорректна."""

    if not url:
        return None

    text = url.strip()
    prefix = "https://stepik.org/users/"

    if not text.startswith(prefix):
        return None

    remainder = text[len(prefix):]
    remainder = remainder.split("?", 1)[0]
    remainder = remainder.strip("/")

    if remainder.endswith("/profile"):
        remainder = remainder[: -len("/profile")]
        remainder = remainder.strip("/")

    user_id_part = remainder

    if not user_id_part.isdigit():
        return None

    return f"{prefix}{int(user_id_part)}"
