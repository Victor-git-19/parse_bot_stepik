"""Генерация мотивационного сообщения на базе OpenAI."""

from __future__ import annotations

from textwrap import dedent

from openai import OpenAI

from app.core.config import settings
from app.parser.stepik_parser import StepikProgress

client = OpenAI(
    api_key=settings.openai_api_key,
    base_url="https://api.aitunnel.ru/v1/",
)


def build_motivation_prompt(progress: StepikProgress) -> str:
    """Собирает подсказку для ИИ с учётом прогресса."""
    return dedent(
        f"""
        Ты — дружественный наставник. Вдохнови пользователя продолжать
        прогресс на Stepik, используй эмодзи, чтобы сообщение выглядело живым.
        Отвечай с юмором и приколом, избегай официального тона.
        Используй шутки и лёгкий стиль общения. Весели плользователя!
        Отвечай ориггинально, не повторяйся. И начинай тоже по разному
        Текущие данные:
        - Решено задач: {progress.solved_tasks}.

        Дай короткое мотивационное сообщение (3-4 предложения),
        без официоза, обязательно вставь несколько эмодзи.
        """
    ).strip()


def generate_motivation(progress: StepikProgress) -> str:
    """Возвращает мотивационное сообщение на основе прогресса."""
    prompt = build_motivation_prompt(progress)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты доброжелательный мотиватор."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=400,
        temperature=0.8,
    )

    return response.choices[0].message.content.strip()
