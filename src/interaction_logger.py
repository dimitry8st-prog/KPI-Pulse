"""Структурированное SQLite-логирование пользовательских взаимодействий."""

from __future__ import annotations

import csv
import hashlib
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"\b\d{6,12}:[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)(api[_ -]?key|token|password)\s*[:=]\s*\S+"),
)


def sanitize(value: Optional[str], limit: int = 4000) -> Optional[str]:
    """Удаляет типовые секреты и ограничивает размер записываемого текста."""
    if value is None:
        return None
    cleaned = value
    for pattern in _SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED]", cleaned)
    return cleaned[:limit]


def anonymize_user_id(user_id: Optional[str]) -> Optional[str]:
    """Возвращает короткий необратимый идентификатор вместо исходного ID."""
    if not user_id:
        return None
    return hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Interaction:
    source: str
    event_type: str
    status: str = "success"
    request: Optional[str] = None
    response: Optional[str] = None
    user_id: Optional[str] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[str] = None


class InteractionLogger:
    """Хранит события AI-чата, Telegram и служебных операций в SQLite."""

    def __init__(self, db_path: str = "./kpi_pulse_logs.db") -> None:
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS interaction_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    request TEXT,
                    response TEXT,
                    user_id_hash TEXT,
                    duration_ms INTEGER,
                    error TEXT,
                    metadata TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_logs_created_at "
                "ON interaction_logs(created_at)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_logs_source_status "
                "ON interaction_logs(source, status)"
            )

    def log(self, interaction: Interaction) -> int:
        """Сохраняет одно событие и возвращает его ID."""
        data = asdict(interaction)
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO interaction_logs (
                    created_at, source, event_type, status, request, response,
                    user_id_hash, duration_ms, error, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    data["source"],
                    data["event_type"],
                    data["status"],
                    sanitize(data["request"]),
                    sanitize(data["response"]),
                    anonymize_user_id(data["user_id"]),
                    data["duration_ms"],
                    sanitize(data["error"], 1000),
                    sanitize(data["metadata"], 2000),
                ),
            )
            return int(cursor.lastrowid)

    def get_stats(self) -> Dict[str, Any]:
        """Возвращает агрегаты для контроля качества и производительности."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) AS total,
                       SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS successful,
                       SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS failed,
                       AVG(duration_ms) AS avg_duration_ms
                FROM interaction_logs
                """
            ).fetchone()
        total = int(row["total"] or 0)
        failed = int(row["failed"] or 0)
        return {
            "total": total,
            "successful": int(row["successful"] or 0),
            "failed": failed,
            "error_rate": round(failed / total * 100, 2) if total else 0.0,
            "avg_duration_ms": round(float(row["avg_duration_ms"] or 0), 2),
        }

    def export_csv(self, output_path: str) -> str:
        """Экспортирует журнал в CSV для анализа и портфолио-демонстрации."""
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM interaction_logs ORDER BY id"
            ).fetchall()
        fieldnames = [column[1] for column in self._table_info()]
        with target.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dict(row) for row in rows)
        return str(target)

    def _table_info(self):
        with self._connect() as conn:
            return conn.execute("PRAGMA table_info(interaction_logs)").fetchall()
