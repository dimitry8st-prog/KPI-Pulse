"""
Модуль LLM-клиента для Claude и GigaChat.
Формирование промптов и генерация дайджестов.
"""

import json
import logging
from typing import Any, Dict, List

import anthropic

from config import CLAUDE_MAX_TOKENS, CLAUDE_MODEL, get_config

logger = logging.getLogger(__name__)


class LLMClient:
    """Клиент для взаимодействия с LLM-провайдерами."""

    def __init__(self, provider: str = "claude") -> None:
        self.config = get_config()
        self.provider = provider or self.config.LLM_PROVIDER
        self._client = None
        self._init_provider()

    def ask(
        self,
        user_question: str,
        context: List[str],
        kpis: Dict[str, Any],
    ) -> str:
        """Формирует промпт и возвращает ответ AI-аналитика."""
        try:
            if not user_question or not user_question.strip():
                return "Пожалуйста, задайте вопрос."

            prompt = self._build_ask_prompt(user_question, context, kpis)
            response = self._call_llm(prompt)
            logger.info("Получен ответ LLM на вопрос: %s", user_question[:50])
            return response
        except Exception as exc:
            logger.error("Ошибка запроса к LLM: %s", exc)
            return f"Не удалось получить ответ от AI: {exc}"

    def generate_digest(
        self, kpis: Dict[str, Any], anomalies: List[Dict[str, Any]]
    ) -> str:
        """Генерирует еженедельный дайджест KPI в формате Markdown."""
        try:
            prompt = self._build_digest_prompt(kpis, anomalies)
            digest = self._call_llm(prompt)
            logger.info("Дайджест сгенерирован")
            return digest
        except Exception as exc:
            logger.error("Ошибка генерации дайджеста: %s", exc)
            return self._fallback_digest(kpis, anomalies)

    def _init_provider(self) -> None:
        """Инициализирует клиент выбранного провайдера."""
        if self.provider == "claude":
            if not self.config.CLAUDE_API_KEY:
                logger.warning("CLAUDE_API_KEY не задан")
            self._client = anthropic.Anthropic(api_key=self.config.CLAUDE_API_KEY)
        elif self.provider == "gigachat":
            if not self.config.GIGACHAT_API_KEY:
                logger.warning("GIGACHAT_API_KEY не задан")
            self._client = None
        else:
            raise ValueError(f"Неизвестный провайдер LLM: {self.provider}")

    def _call_llm(self, user_prompt: str) -> str:
        """Вызывает LLM API и возвращает текст ответа."""
        if self.provider == "claude":
            return self._call_claude(user_prompt)
        if self.provider == "gigachat":
            return self._call_gigachat(user_prompt)
        raise ValueError(f"Провайдер не поддерживается: {self.provider}")

    def _call_claude(self, user_prompt: str) -> str:
        """Запрос к Anthropic Claude API."""
        if not self.config.CLAUDE_API_KEY:
            raise ValueError(
                "CLAUDE_API_KEY не задан. Добавьте ключ в файл .env"
            )
        try:
            message = self._client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                system=self.config.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text
        except anthropic.AuthenticationError as exc:
            logger.error("Ошибка аутентификации Claude: %s", exc)
            raise ValueError("Неверный CLAUDE_API_KEY") from exc
        except Exception as exc:
            logger.error("Ошибка Claude API: %s", exc)
            raise

    def _call_gigachat(self, user_prompt: str) -> str:
        """Заглушка для GigaChat — требует отдельной интеграции."""
        logger.warning("GigaChat: используется fallback-ответ")
        return (
            "GigaChat API не настроен. "
            "Укажите GIGACHAT_API_KEY и реализуйте интеграцию, "
            "или переключитесь на LLM_PROVIDER=claude.\n\n"
            f"Запрос: {user_prompt[:200]}..."
        )

    def _build_ask_prompt(
        self,
        user_question: str,
        context: List[str],
        kpis: Dict[str, Any],
    ) -> str:
        """Собирает промпт для AI-аналитика."""
        context_text = "\n".join(context) if context else "Контекст не найден."
        kpi_text = json.dumps(kpis, ensure_ascii=False, indent=2)
        return (
            f"Контекст из базы данных:\n{context_text}\n\n"
            f"Текущие KPI:\n{kpi_text}\n\n"
            f"Вопрос пользователя: {user_question}"
        )

    def _build_digest_prompt(
        self, kpis: Dict[str, Any], anomalies: List[Dict[str, Any]]
    ) -> str:
        """Собирает промпт для еженедельного дайджеста."""
        deltas = kpis.get("deltas", {})
        anomaly_text = (
            json.dumps(anomalies, ensure_ascii=False, indent=2)
            if anomalies
            else "Аномалий не обнаружено."
        )
        period = kpis.get("month", "N/A")
        return (
            f"Сформируй дайджест KPI за {period} для Telegram в формате Markdown.\n"
            "Включи:\n"
            "1. Заголовок с указанием месяца\n"
            "2. Изменения KPI с процентами и стрелками ↑↓ (к предыдущему месяцу)\n"
            "3. Найденные аномалии за этот период\n"
            "4. Одну главную рекомендацию\n\n"
            f"Текущие KPI: {json.dumps(kpis, ensure_ascii=False, indent=2)}\n"
            f"Дельты: {json.dumps(deltas, ensure_ascii=False, indent=2)}\n"
            f"Аномалии: {anomaly_text}"
        )

    def _fallback_digest(
        self, kpis: Dict[str, Any], anomalies: List[Dict[str, Any]]
    ) -> str:
        """Fallback-дайджест без LLM."""
        deltas = kpis.get("deltas", {})
        lines = [
            "📊 *Еженедельный дайджест KPI*",
            f"📅 Период: {kpis.get('month', 'N/A')}",
            "",
            "*KPI:*",
            f"• CAC: {kpis.get('cac', 0)} руб. {self._delta_arrow(deltas.get('cac'))}",
            f"• LTV: {kpis.get('ltv', 0)} руб. {self._delta_arrow(deltas.get('ltv'))}",
            f"• MRR: {kpis.get('mrr', 0)} руб. {self._delta_arrow(deltas.get('mrr'))}",
            f"• Churn: {kpis.get('churn', 0)}% {self._delta_arrow(deltas.get('churn'))}",
            f"• Conversion: {kpis.get('conversion', 0)}% {self._delta_arrow(deltas.get('conversion'))}",
            "",
        ]
        if anomalies:
            lines.append("*Аномалии:*")
            for a in anomalies[:5]:
                lines.append(
                    f"• {a['metric']} ({a['month']}): {a['value']} — {a['reason']}"
                )
        else:
            lines.append("*Аномалий не обнаружено.*")
        lines.append("")
        lines.append(
            "💡 *Рекомендация:* Проанализируйте рост CAC и оптимизируйте маркетинговые каналы."
        )
        return "\n".join(lines)

    def _delta_arrow(self, delta: float | None) -> str:
        """Форматирует дельту со стрелкой."""
        if delta is None:
            return ""
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        return f"({arrow} {abs(delta):.1f}%)"
