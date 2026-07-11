"""
Точка входа Telegram-бота KPI Pulse.
Запускает планировщик еженедельных дайджестов.
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import get_config
from src.data_loader import DataLoader
from src.kpi_calculator import KPICalculator
from src.llm_client import LLMClient
from src.telegram_bot import TelegramDigestBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

SAMPLE_DATA_PATH = Path(__file__).parent / "data" / "sample_data.csv"


def generate_weekly_digest(month: str | None = None) -> dict:
    """Генерирует дайджест на основе sample_data за указанный месяц."""
    try:
        loader = DataLoader()
        df = loader.load_csv(str(SAMPLE_DATA_PATH))
        is_valid, missing = loader.validate_schema(df)

        if not is_valid:
            logger.error("Невалидная схема данных: %s", missing)
            return {"digest": "", "error": f"Отсутствуют столбцы: {missing}"}

        calculator = KPICalculator()
        kpis = calculator.calculate_all(df, target_month=month)
        anomalies = calculator.detect_anomalies(df)
        if month:
            anomalies = calculator.filter_anomalies_for_month(anomalies, month)

        llm = LLMClient(provider=get_config().LLM_PROVIDER)
        digest = llm.generate_digest(kpis, anomalies)

        return {"digest": digest, "kpis": kpis, "anomalies": anomalies}
    except Exception as exc:
        logger.error("Ошибка генерации дайджеста: %s", exc)
        return {"digest": "", "error": str(exc)}


def main() -> None:
    """Запускает Telegram-бот с еженедельным планировщиком."""
    logger.info("Запуск KPI Pulse Telegram Bot...")
    config = get_config()

    if not config.TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN не задан. Завершение работы.")
        sys.exit(1)

    bot = TelegramDigestBot()
    logger.info(
        "Бот запускается. Дайджест по расписанию — каждый понедельник в 09:00."
    )
    bot.run(generate_weekly_digest)


if __name__ == "__main__":
    main()
