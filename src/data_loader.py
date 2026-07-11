"""
Модуль загрузки данных из CSV и Google Sheets.
Валидация схемы и автоопределение структуры датасета.
"""

import logging
import re
from typing import Any, Dict, List, Tuple

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from config import REQUIRED_COLUMNS, get_config

logger = logging.getLogger(__name__)


class DataLoader:
    """Загрузчик и валидатор бизнес-данных KPI."""

    def __init__(self) -> None:
        self.config = get_config()

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Загружает данные из CSV-файла."""
        try:
            df = pd.read_csv(file_path)
            logger.info("Загружено %d строк из CSV: %s", len(df), file_path)
            return self._enforce_row_limit(df)
        except FileNotFoundError as exc:
            logger.error("Файл не найден: %s", file_path)
            raise FileNotFoundError(f"Файл не найден: {file_path}") from exc
        except pd.errors.EmptyDataError as exc:
            logger.error("CSV-файл пуст: %s", file_path)
            raise ValueError(f"CSV-файл пуст: {file_path}") from exc
        except Exception as exc:
            logger.error("Ошибка чтения CSV: %s", exc)
            raise ValueError(f"Не удалось прочитать CSV: {exc}") from exc

    def load_google_sheets(self, sheet_url: str) -> pd.DataFrame:
        """Загружает данные из Google Sheets по URL."""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                "credentials.json", scope
            )
            client = gspread.authorize(credentials)
            sheet_id = self._extract_sheet_id(sheet_url)
            spreadsheet = client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            records = worksheet.get_all_records()
            df = pd.DataFrame(records)
            logger.info("Загружено %d строк из Google Sheets", len(df))
            return self._enforce_row_limit(df)
        except FileNotFoundError as exc:
            logger.error("Файл credentials.json не найден")
            raise FileNotFoundError(
                "Файл credentials.json не найден. "
                "Создайте сервисный аккаунт Google Cloud."
            ) from exc
        except Exception as exc:
            logger.error("Ошибка загрузки Google Sheets: %s", exc)
            raise ValueError(f"Не удалось загрузить Google Sheets: {exc}") from exc

    def validate_schema(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Проверяет наличие обязательных столбцов в датафрейме."""
        try:
            if df is None or df.empty:
                return False, list(REQUIRED_COLUMNS)
            missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            is_valid = len(missing) == 0
            if not is_valid:
                logger.warning("Отсутствуют столбцы: %s", missing)
            return is_valid, missing
        except Exception as exc:
            logger.error("Ошибка валидации схемы: %s", exc)
            return False, list(REQUIRED_COLUMNS)

    def detect_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Автоопределение типов столбцов, диапазона дат и количества строк."""
        try:
            if df is None or df.empty:
                return {"row_count": 0, "columns": {}, "date_range": None}

            column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
            date_range = self._detect_date_range(df)
            structure = {
                "row_count": len(df),
                "columns": column_types,
                "date_range": date_range,
            }
            logger.info("Структура данных: %d строк", structure["row_count"])
            return structure
        except Exception as exc:
            logger.error("Ошибка определения структуры: %s", exc)
            raise ValueError(f"Не удалось определить структуру данных: {exc}") from exc

    def _enforce_row_limit(self, df: pd.DataFrame) -> pd.DataFrame:
        """Проверяет лимит строк и возвращает датафрейм."""
        if len(df) > self.config.MAX_ROWS:
            msg = (
                f"Превышен лимит строк: {len(df)} > {self.config.MAX_ROWS}. "
                "Уменьшите объём данных или измените MAX_ROWS в .env."
            )
            logger.error(msg)
            raise ValueError(msg)
        return df

    def _extract_sheet_id(self, sheet_url: str) -> str:
        """Извлекает ID таблицы из URL Google Sheets."""
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
        if not match:
            raise ValueError(f"Некорректный URL Google Sheets: {sheet_url}")
        return match.group(1)

    def _detect_date_range(self, df: pd.DataFrame) -> Dict[str, str] | None:
        """Определяет диапазон дат по столбцу month."""
        if "month" not in df.columns:
            return None
        try:
            dates = pd.to_datetime(df["month"], errors="coerce").dropna()
            if dates.empty:
                return None
            return {
                "start": dates.min().strftime("%Y-%m"),
                "end": dates.max().strftime("%Y-%m"),
            }
        except Exception as exc:
            logger.warning("Не удалось определить диапазон дат: %s", exc)
            return None
