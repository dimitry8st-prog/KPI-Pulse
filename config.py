"""
Модуль конфигурации KPI Pulse.
Загружает настройки из переменных окружения и предоставляет dataclass Config.
"""

import logging
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEXT = (
    "Ты — AI-аналитик KPI компании. У тебя есть доступ "
    "к данным о продажах, маркетинге и клиентах.\n\n"
    "Правила ответа:\n"
    "1. Всегда приводи конкретные цифры из данных\n"
    "2. Объясняй простым языком, без жаргона\n"
    "3. Каждый ответ заканчивай рекомендацией (1-2 предложения)\n"
    "4. Если данных недостаточно — честно скажи об этом "
    "и укажи, какие данные нужны\n"
    "5. Отвечай только на русском языке\n"
    "6. Формат: цифры → пояснение → рекомендация"
)

REQUIRED_COLUMNS = [
    "month",
    "new_customers",
    "lost_customers",
    "revenue",
    "marketing_spend",
    "total_customers",
    "deals_closed",
    "deals_total",
]

KPI_METRICS = ["cac", "ltv", "mrr", "churn", "conversion"]

DEFAULT_LIFESPAN_MONTHS = 24

WEEKLY_DIGEST_HOUR = 9
WEEKLY_DIGEST_MINUTE = 0
WEEKLY_DIGEST_DAY = "mon"

CLAUDE_MODEL = "claude-sonnet-4-6"
CLAUDE_MAX_TOKENS = 2048

CHROMA_COLLECTION_NAME = "kpi_data"

TERMS_ACCEPTED_KEY = "terms_accepted"


@dataclass
class Config:
    """Конфигурация приложения KPI Pulse."""

    LLM_PROVIDER: str = "claude"
    CLAUDE_API_KEY: str = ""
    GIGACHAT_API_KEY: str = ""
    TELEGRAM_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    CHROMA_DB_PATH: str = "./chroma_db"
    SQLITE_DB_PATH: str = "./kpi_pulse.db"
    LOG_DB_PATH: str = "./kpi_pulse_logs.db"
    MAX_ROWS: int = 5000
    SYSTEM_PROMPT: str = field(default_factory=lambda: SYSTEM_PROMPT_TEXT)

    @classmethod
    def from_env(cls) -> "Config":
        """Создаёт конфигурацию из переменных окружения."""
        try:
            return cls(
                LLM_PROVIDER=os.getenv("LLM_PROVIDER", "claude"),
                CLAUDE_API_KEY=os.getenv("CLAUDE_API_KEY", ""),
                GIGACHAT_API_KEY=os.getenv("GIGACHAT_API_KEY", ""),
                TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN", ""),
                TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID", ""),
                CHROMA_DB_PATH=os.getenv("CHROMA_DB_PATH", "./chroma_db"),
                SQLITE_DB_PATH=os.getenv("SQLITE_DB_PATH", "./kpi_pulse.db"),
                LOG_DB_PATH=os.getenv("LOG_DB_PATH", "./kpi_pulse_logs.db"),
                MAX_ROWS=int(os.getenv("MAX_ROWS", "5000")),
                SYSTEM_PROMPT=os.getenv("SYSTEM_PROMPT", SYSTEM_PROMPT_TEXT),
            )
        except ValueError as exc:
            logger.error("Ошибка загрузки конфигурации: %s", exc)
            raise ValueError(f"Некорректные значения в .env: {exc}") from exc


def get_config() -> Config:
    """Возвращает singleton-конфигурацию приложения."""
    return Config.from_env()
