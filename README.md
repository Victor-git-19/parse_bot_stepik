# Stepik Motivation Bot

[![CI](https://github.com/Victor-git-19/parse_bot_stepik/actions/workflows/main.yml/badge.svg)](https://github.com/Victor-git-19/parse_bot_stepik/actions/workflows/main.yml)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-enabled-4169E1?logo=postgresql&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)
![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot-@-26A5E4?logo=telegram&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-powered-412991?logo=openai&logoColor=white)

Телеграм‑бот, который:

- принимает ссылку на профиль Stepik, сохраняет её в базе и отслеживает прогресс;
- по запросу `/progress` забирает статистику через Stepik API и обновляет её в БД;
- генерирует мотивационные сообщения через OpenAI API и отправляет пользователю;
- поддерживает хранение данных как в локальном SQLite, так и в PostgreSQL (docker-compose);
- автоматизирует миграции через Alembic при каждом запуске.

## Стек

- Python 3.13, `pyTelegramBotAPI`, `aiohttp`, `SQLAlchemy 2`, `asyncpg`;
- Alembic для версионирования схемы;
- OpenAI SDK для генерации текста;
- Docker / docker-compose для изоляции и PostgreSQL;
- GitHub Actions (`.github/workflows/main.yml`) запускает `pytest` и публикует образ в Docker Hub.

## Структура проекта

```
app/
├─ bot/          # телеграм-хендлеры
├─ core/         # конфиг, база, declarative Base
├─ crud/         # асинхронные операции с моделью User
├─ models/       # ORM-модели
├─ parser/       # работа с Stepik API
├─ motivation_ai/# генерация промптов/ответов OpenAI
└─ utils/        # вспомогательные функции (нормализация URL и т.п.)
tests/           # pytest-юниты
alembic/         # миграции
Dockerfile       # образ приложения
docker-compose.yml
docker-entrypoint.sh
```

## Переменные окружения

Создай `.env` (по умолчанию игнорируется git’ом):

```
TELEGRAM_TOKEN=123:ABC
DATABASE_URL=sqlite+aiosqlite:///./telebot.db
OPENAI_API_KEY=sk-...
POSTGRES_DB=telebot
POSTGRES_USER=telebot
POSTGRES_PASSWORD=telebot
```

`DATABASE_URL` можно переключить на Postgres: `postgresql+asyncpg://telebot:telebot@db:5432/telebot`.

## Локальный запуск (SQLite)

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

alembic upgrade head     # создаёт таблицы в telebot.db
python -m app.bot.bot    # запускает асинхронный бот
```

## Docker

### Быстрый запуск (SQLite внутри контейнера)

```bash
docker build -t stepik-bot .
docker run --env-file .env \
  -v $(pwd)/telebot.db:/app/telebot.db \
  stepik-bot
```

`docker-entrypoint.sh` автоматически применяет `alembic upgrade head` перед запуском.

### docker-compose + PostgreSQL

1. В `.env` пропиши `DATABASE_URL=postgresql+asyncpg://telebot:telebot@db:5432/telebot`.
2. Запусти сервисы:
   ```bash
   docker compose up -d
   ```
   Compose создаст контейнеры `telebot_db` (Postgres 13) и `telebot_app` (образ `victorgtr/telebot_app` или локальная сборка).
3. Логи:
   ```bash
   docker compose logs -f bot
   docker compose logs -f db
   ```
4. Остановить: `docker compose down` (флаг `-v`, чтобы стереть volume `db_data`).

## Тесты и линтеры

```bash
pytest                  # юнит-тесты из каталога tests/
flake8 app tests        # статический анализ / стиль
```

CI в GitHub Actions повторяет эти шаги. При успешном пуше в `main` workflow дополнительно собирает Docker-образ и публикует его в Docker Hub (нужны секреты `DOCKER_USERNAME` и `DOCKER_PASSWORD`).

## Работа с миграциями

Создать новую ревизию:

```bash
alembic revision --autogenerate -m "description"
```

Применить:

```bash
alembic upgrade head
```

В docker-контейнерах это делает `docker-entrypoint.sh`.

## Полезные команды

| Команда | Описание |
| --- | --- |
| `python -m app.bot.bot` | запуск бота в текущем окружении |
| `pytest -q` | быстрый прогон тестов |
| `docker compose up --build` | пересборка и поднятие сервисов с Postgres |
| `docker compose run --rm bot alembic upgrade head` | ручное применение миграций внутри Compose |

## Примечания

- Stepik REST API используется без ключей; при ошибках выбрасывается `StepikParserError`.
- Мотивационные сообщения генерируются через кастомный `base_url` (см. `app/motivation_ai/motivation.py`); обнови при необходимости.
- `.dockerignore` и `.gitignore` настроены так, чтобы не включать `venv`, `.env`, временные базы и IDE-файлы в образ/репозиторий.

---
Автор — [Виктор Смирнов](https://github.com/Victor-git-19)
