"""Получение прогресса Stepik через публичное API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class StepikParserError(Exception):
    """Общий сбой парсера Stepik."""


@dataclass
class StepikProgress:
    """Статистика активности пользователя Stepik."""

    solved_tasks: int


def _extract_user_id(stepik_url: str) -> int:
    """Возвращает числовой идентификатор пользователя из URL."""
    prefix = "https://stepik.org/users/"
    if not stepik_url.startswith(prefix):
        raise StepikParserError("Некорректный формат ссылки Stepik.")

    remainder = stepik_url[len(prefix) :].strip("/")
    remainder = remainder.split("?", 1)[0]

    if not remainder.isdigit():
        raise StepikParserError("Не удалось определить ID пользователя Stepik.")

    return int(remainder)


def _fetch_user_payload(user_id: int, *, timeout: int) -> dict[str, Any]:
    """Запрашивает данные пользователя из API Stepik."""
    url = f"https://stepik.org/api/users/{user_id}"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise StepikParserError("Stepik API недоступно.") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise StepikParserError("Stepik API вернуло неожиданный ответ.") from exc

    users = payload.get("users") or []
    if not users:
        raise StepikParserError("Stepik API не вернуло данные о пользователе.")

    return users[0]


def fetch_stepik_progress(stepik_url: str, timeout: int = 10) -> StepikProgress:
    """Возвращает прогресс пользователя по ссылке профиля."""
    user_id = _extract_user_id(stepik_url)
    user_payload = _fetch_user_payload(user_id, timeout=timeout)

    solved_steps = user_payload.get("solved_steps_count")
    if solved_steps is None:
        raise StepikParserError("Stepik API не содержит solved_steps_count.")

    return StepikProgress(solved_tasks=int(solved_steps))
