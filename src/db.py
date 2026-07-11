"""
SQLite-хранилище для истории диалогов и настроек пользователя.
"""

import logging
import sqlite3
from typing import Any, Dict, List

from config import TERMS_ACCEPTED_KEY, get_config

logger = logging.getLogger(__name__)


class ChatDatabase:
    """Управление SQLite-базой для чата и настроек."""

    def __init__(self) -> None:
        self.config = get_config()
        self.db_path = self.config.SQLITE_DB_PATH
        self._init_db()

    def _init_db(self) -> None:
        """Создаёт таблицы при первом запуске."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
            logger.info("SQLite база инициализирована: %s", self.db_path)
        except sqlite3.Error as exc:
            logger.error("Ошибка инициализации SQLite: %s", exc)
            raise RuntimeError(f"Не удалось инициализировать БД: {exc}") from exc

    def is_terms_accepted(self) -> bool:
        """Проверяет, принял ли пользователь условия использования."""
        return self.get_setting(TERMS_ACCEPTED_KEY) == "true"

    def accept_terms(self) -> None:
        """Сохраняет флаг принятия условий."""
        self.set_setting(TERMS_ACCEPTED_KEY, "true")

    def get_setting(self, key: str) -> str | None:
        """Получает значение настройки по ключу."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT value FROM settings WHERE key = ?", (key,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error as exc:
            logger.error("Ошибка чтения настройки %s: %s", key, exc)
            return None

    def set_setting(self, key: str, value: str) -> None:
        """Сохраняет значение настройки."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, value),
                )
                conn.commit()
        except sqlite3.Error as exc:
            logger.error("Ошибка записи настройки %s: %s", key, exc)

    def save_message(self, role: str, content: str) -> None:
        """Сохраняет сообщение в историю чата."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO chat_history (role, content) VALUES (?, ?)",
                    (role, content),
                )
                conn.commit()
        except sqlite3.Error as exc:
            logger.error("Ошибка сохранения сообщения: %s", exc)

    def load_history(self) -> List[Dict[str, str]]:
        """Загружает историю чата из базы."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT role, content FROM chat_history ORDER BY id"
                )
                return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            logger.error("Ошибка загрузки истории: %s", exc)
            return []

    def clear_history(self) -> None:
        """Очищает историю чата."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM chat_history")
                conn.commit()
            logger.info("История чата очищена")
        except sqlite3.Error as exc:
            logger.error("Ошибка очистки истории: %s", exc)
