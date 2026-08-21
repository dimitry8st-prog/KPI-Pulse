"""
Модуль Telegram-бота для отправки еженедельных KPI-дайджестов.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot, Update
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes

from config import (
    WEEKLY_DIGEST_DAY,
    WEEKLY_DIGEST_HOUR,
    WEEKLY_DIGEST_MINUTE,
    get_config,
)
from src.interaction_logger import Interaction, InteractionLogger

logger = logging.getLogger(__name__)

START_MESSAGE = (
    "👋 Привет! Я *KPI Pulse* — бот для аналитики бизнес-метрик.\n\n"
    "*Команды:*\n"
    "/start — это сообщение\n"
    "/digest — дайджест за последний месяц\n"
    "/digest 2026-06 — дайджест за конкретный месяц\n\n"
    "📅 Автоматический дайджест отправляется каждый понедельник в 09:00."
)


class TelegramDigestBot:
    """Бот для отправки KPI-дайджестов в Telegram."""

    def __init__(self) -> None:
        self.config = get_config()
        self.interaction_logger = InteractionLogger(self.config.LOG_DB_PATH)
        self._scheduler: Optional[BackgroundScheduler] = None
        self._digest_func: Optional[Callable[..., Dict[str, Any]]] = None
        self._app: Optional[Application] = None

    def run(self, digest_func: Callable[..., Dict[str, Any]]) -> None:
        """Запускает polling и еженедельный планировщик."""
        if not self.config.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN не задан. Проверьте .env")

        self._digest_func = digest_func
        self.schedule_weekly(digest_func)

        self._app = (
            Application.builder()
            .token(self.config.TELEGRAM_TOKEN)
            .build()
        )
        self._app.add_handler(CommandHandler("start", self._handle_start))
        self._app.add_handler(CommandHandler("digest", self._handle_digest))

        logger.info("Запуск polling — бот слушает команды...")
        self._app.run_polling(drop_pending_updates=True)

    def send_digest(self, digest_text: str, chat_id: Optional[str] = None) -> bool:
        """Отправляет сформированный дайджест в чат."""
        try:
            if not digest_text or not digest_text.strip():
                logger.warning("Пустой текст дайджеста — отправка отменена")
                return False

            target_chat = chat_id or self.config.TELEGRAM_CHAT_ID
            if not target_chat or not self.config.TELEGRAM_TOKEN:
                logger.error("TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не заданы")
                return False

            asyncio.run(
                self._send_message_async(target_chat, digest_text)
            )
            logger.info("Дайджест отправлен в чат %s", target_chat)
            return True
        except TelegramError as exc:
            logger.error("Ошибка Telegram API: %s", exc)
            return False
        except Exception as exc:
            logger.error("Ошибка отправки дайджеста: %s", exc)
            return False

    def schedule_weekly(self, kpi_func: Callable[..., Dict[str, Any]]) -> None:
        """Планирует еженедельную отправку дайджеста (понедельник, 09:00)."""
        try:
            if self._scheduler is None:
                self._scheduler = BackgroundScheduler()
                self._scheduler.start()

            self._scheduler.add_job(
                func=lambda: self._run_scheduled_digest(kpi_func),
                trigger=CronTrigger(
                    day_of_week=WEEKLY_DIGEST_DAY,
                    hour=WEEKLY_DIGEST_HOUR,
                    minute=WEEKLY_DIGEST_MINUTE,
                ),
                id="weekly_kpi_digest",
                replace_existing=True,
            )
            logger.info(
                "Планировщик настроен: каждый %s в %02d:%02d",
                WEEKLY_DIGEST_DAY,
                WEEKLY_DIGEST_HOUR,
                WEEKLY_DIGEST_MINUTE,
            )
        except Exception as exc:
            logger.error("Ошибка настройки планировщика: %s", exc)
            raise RuntimeError(f"Не удалось настроить планировщик: {exc}") from exc

    async def _handle_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /start."""
        try:
            started_at = time.perf_counter()
            if update.message:
                await update.message.reply_text(
                    START_MESSAGE, parse_mode="Markdown"
                )
                logger.info("Команда /start от chat_id=%s", update.effective_chat.id)
                self.interaction_logger.log(Interaction(
                    source="telegram", event_type="command_start",
                    request="/start", user_id=str(update.effective_chat.id),
                    duration_ms=int((time.perf_counter() - started_at) * 1000),
                ))
        except Exception as exc:
            logger.error("Ошибка обработки /start: %s", exc)

    async def _handle_digest(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /digest — отправка дайджеста по запросу."""
        try:
            started_at = time.perf_counter()
            if not update.message or not self._digest_func:
                return

            month = context.args[0] if context.args else None
            period_label = f" за {month}" if month else ""
            await update.message.reply_text(f"⏳ Формирую KPI-дайджест{period_label}...")

            result = self._digest_func(month)
            digest_text = result.get("digest", "")
            error = result.get("error")

            if error:
                await update.message.reply_text(f"❌ Ошибка: {error}")
                self.interaction_logger.log(Interaction(
                    source="telegram", event_type="command_digest", status="error",
                    request=f"/digest {month or ''}".strip(),
                    user_id=str(update.effective_chat.id),
                    duration_ms=int((time.perf_counter() - started_at) * 1000),
                    error=str(error),
                ))
                return

            if not digest_text:
                await update.message.reply_text("❌ Дайджест пуст.")
                return

            await update.message.reply_text(digest_text, parse_mode="Markdown")
            logger.info("Дайджест отправлен по /digest в chat_id=%s", update.effective_chat.id)
            self.interaction_logger.log(Interaction(
                source="telegram", event_type="command_digest",
                request=f"/digest {month or ''}".strip(), response=digest_text,
                user_id=str(update.effective_chat.id),
                duration_ms=int((time.perf_counter() - started_at) * 1000),
            ))
        except Exception as exc:
            logger.error("Ошибка обработки /digest: %s", exc)
            self.interaction_logger.log(Interaction(
                source="telegram", event_type="command_digest", status="error",
                request="/digest",
                user_id=str(update.effective_chat.id) if update.effective_chat else None,
                error=str(exc),
            ))
            if update.message:
                await update.message.reply_text(f"❌ Не удалось сформировать дайджест: {exc}")

    def _run_scheduled_digest(
        self, kpi_func: Callable[..., Dict[str, Any]]
    ) -> None:
        """Выполняет запланированную отправку дайджеста."""
        try:
            result = kpi_func()
            digest_text = result.get("digest", "")
            if digest_text:
                self.send_digest(digest_text)
            else:
                logger.warning("Планировщик: пустой дайджест")
        except Exception as exc:
            logger.error("Ошибка в запланированной задаче: %s", exc)

    async def _send_message_async(self, chat_id: str, text: str) -> None:
        """Асинхронная отправка сообщения через Bot API."""
        async with Bot(token=self.config.TELEGRAM_TOKEN) as bot:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown",
            )
