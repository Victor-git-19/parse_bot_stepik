import asyncio
from typing import Optional

from telebot.async_telebot import AsyncTeleBot

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.crud.user import (
    create_user,
    get_user_by_tg_id,
    update_user_progress,
)
from app.motivation_ai.motivation import generate_motivation
from app.parser.stepik_parser import (
    StepikParserError,
    StepikProgress,
    fetch_stepik_progress,
)
from app.utils.url_to_norm import normalize_stepik_url


bot = AsyncTeleBot(settings.telegram_token)


@bot.message_handler(commands=["start"])
async def start_handler(message):
    tg_user = message.from_user
    first_name = tg_user.first_name or "друг"
    await bot.send_message(
        message.chat.id,
        f"Привет, {first_name}! Отправь ссылку на профиль Stepik",
    )


@bot.message_handler(
    content_types=["text"],
    func=lambda message: not (message.text or "").startswith("/"),
)
async def text_handler(message):
    normalized_url: Optional[str] = normalize_stepik_url(message.text or "")

    if not normalized_url:
        await bot.send_message(
            message.chat.id,
            "Некорректный формат ссылки.",
        )
        return

    name = message.from_user.first_name or "друг"

    try:
        async with AsyncSessionLocal() as session:
            await create_user(
                session=session,
                tg_id=message.from_user.id,
                name=name,
                stepik_url=normalized_url,
            )
    except Exception as exc:
        print(f"DB error: {exc}")
        await bot.send_message(
            message.chat.id,
            "Не удалось сохранить ссылку. Попробуй позже.",
        )
        return

    await bot.send_message(
        message.chat.id,
        f"Спасибо, {name}! "
        f"Твой Stepik профиль {normalized_url} сохранён.",
    )


@bot.message_handler(commands=["progress"])
async def progress_handler(message):
    async with AsyncSessionLocal() as session:
        user = await get_user_by_tg_id(session, message.from_user.id)

    if not user or not user.stepik_url:
        await bot.send_message(
            message.chat.id,
            "Сначала отправь ссылку на профиль Stepik, чтобы я знал, "
            "что парсить.",
        )
        return

    try:
        progress = fetch_stepik_progress(user.stepik_url)
    except StepikParserError as exc:
        print(f"Parser error: {exc}")
        await bot.send_message(
            message.chat.id,
            "Не удалось получить прогресс со Stepik. Попробуй позже.",
        )
        return

    async with AsyncSessionLocal() as session:
        await update_user_progress(
            session,
            tg_id=message.from_user.id,
            solved_tasks=progress.solved_tasks,
            current_streak=progress.current_streak,
            max_streak=progress.max_streak,
        )

    motivation = generate_motivation(
        StepikProgress(
            current_streak=progress.current_streak,
            max_streak=progress.max_streak,
            solved_tasks=progress.solved_tasks,
        )
    )

    await bot.send_message(
        message.chat.id,
        "Твой прогресс на Stepik:\n"
        f"• Дней подряд: {progress.current_streak}\n"
        f"• Рекорд: {progress.max_streak}\n"
        f"• Задач решено: {progress.solved_tasks}\n\n"
        f"{motivation}\n\n"
        "Если нужна помощь или идеи для прокачки, пиши моему другу "
        "@Prompt_ikBot — он поможет!",
    )


async def run_bot():
    await bot.infinity_polling()

if __name__ == "__main__":
    asyncio.run(run_bot())
