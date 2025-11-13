"""Парсер прогресса Stepik через Selenium."""

from __future__ import annotations

import os
from dataclasses import dataclass
from time import sleep
from typing import Dict, Literal, Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class StepikParserError(Exception):
    """Общий сбой парсера Stepik."""


@dataclass
class StepikProgress:
    """Статистика активности пользователя Stepik."""

    current_streak: int
    max_streak: int
    solved_tasks: int


def _parse_int(text: str) -> int:
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else 0


def _wait_for_values(driver: webdriver.Remote, attempts: int = 5) -> None:
    """Дополнительное ожидание, пока цифры появятся в блоках."""
    for _ in range(attempts):
        values = driver.find_elements(
            By.CSS_SELECTOR,
            "dl.last-activity-stats .last-activity-stats__value",
        )
        if any(ch.isdigit() for el in values for ch in el.text):
            return
        sleep(0.5)


def _create_driver() -> webdriver.Remote:
    """Создаёт Selenium driver для локальной или удалённой среды."""
    selenium_url = os.getenv("SELENIUM_URL")
    if selenium_url:
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Remote(
            command_executor=selenium_url,
            options=options,
        )

    # локальная разработка (macOS Safari)
    return webdriver.Safari()


def fetch_stepik_progress(
    stepik_url: str,
    driver: Optional[webdriver.Remote] = None,
    timeout: int = 20,
) -> StepikProgress:
    """Возвращает прогресс пользователя по ссылке профиля."""
    driver_provided = driver is not None
    if driver is None:
        driver = _create_driver()

    wait = WebDriverWait(driver, timeout)

    try:
        driver.get(stepik_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        stats_blocks = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "dl.last-activity-stats div")
            )
        )
        _wait_for_values(driver)

        metrics: Dict[Literal["cur", "max", "tasks"], int] = {
            "cur": 0,
            "max": 0,
            "tasks": 0,
        }

        for block in stats_blocks:
            value_el = block.find_element(
                By.CLASS_NAME,
                "last-activity-stats__value",
            )
            desc_el = block.find_element(
                By.CLASS_NAME,
                "last-activity-stats__desc",
            )
            value = _parse_int(value_el.text)
            desc = desc_el.text.lower()

            if "макс" in desc:
                metrics["max"] = value
            elif "без перерыва" in desc:
                metrics["cur"] = value
            elif "задач" in desc or "задача" in desc:
                metrics["tasks"] = value

        return StepikProgress(
            current_streak=metrics["cur"],
            max_streak=metrics["max"],
            solved_tasks=metrics["tasks"],
        )
    except TimeoutException as exc:
        raise StepikParserError(
            "Не удалось дождаться блока статистики Stepik."
        ) from exc
    except Exception as exc:
        raise StepikParserError("Сбой при парсинге Stepik.") from exc
    finally:
        if not driver_provided:
            driver.quit()
