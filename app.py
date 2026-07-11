"""
Streamlit-приложение KPI Pulse.
Дашборд KPI, AI-аналитик и управление данными.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).parent))

from config import get_config
from src.data_loader import DataLoader
from src.db import ChatDatabase
from src.kpi_calculator import KPICalculator
from src.llm_client import LLMClient
from src.rag_engine import RAGEngine
from src.telegram_bot import TelegramDigestBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

SAMPLE_DATA_PATH = Path(__file__).parent / "data" / "sample_data.csv"


def init_session_state() -> None:
    """Инициализирует session_state Streamlit."""
    defaults = {
        "df": None,
        "kpis": None,
        "anomalies": [],
        "chat_history": [],
        "data_loaded": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_sample_data() -> None:
    """Загружает тестовые данные при первом запуске."""
    if st.session_state.data_loaded:
        return
    try:
        loader = DataLoader()
        df = loader.load_csv(str(SAMPLE_DATA_PATH))
        is_valid, _ = loader.validate_schema(df)
        if is_valid:
            process_data(df)
            st.session_state.data_loaded = True
    except Exception as exc:
        logger.error("Ошибка загрузки sample_data: %s", exc)


def process_data(df: pd.DataFrame) -> None:
    """Обрабатывает данные: KPI, аномалии, индексация RAG."""
    try:
        calculator = KPICalculator()
        kpis = calculator.calculate_all(df)
        anomalies = calculator.detect_anomalies(df)

        rag = RAGEngine()
        rag.index_data(df, kpis)

        st.session_state.df = df
        st.session_state.kpis = kpis
        st.session_state.anomalies = anomalies
        logger.info("Данные обработаны успешно")
    except Exception as exc:
        logger.error("Ошибка обработки данных: %s", exc)
        st.error(f"Ошибка обработки данных: {exc}")


def show_terms_modal(db: ChatDatabase) -> None:
    """Показывает модальное окно принятия условий."""
    if db.is_terms_accepted():
        return

    @st.dialog("Условия использования")
    def terms_dialog() -> None:
        st.markdown(
            "**KPI Pulse** — локальный AI-агент для аналитики KPI.\n\n"
            "- Данные хранятся только на вашем компьютере\n"
            "- API-ключи используются для Claude и Telegram\n"
            "- Вы несёте ответственность за конфиденциальность данных"
        )
        if st.button("Принимаю условия", type="primary"):
            db.accept_terms()
            st.rerun()

    terms_dialog()


def render_data_tab() -> None:
    """Таб загрузки и превью данных."""
    st.header("📁 Данные")
    loader = DataLoader()

    uploaded = st.file_uploader("Загрузить CSV", type=["csv"])
    sheet_url = st.text_input("URL Google Sheets", placeholder="https://docs.google.com/spreadsheets/d/...")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Загрузить CSV") and uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
                if len(df) > get_config().MAX_ROWS:
                    st.error(f"Превышен лимит {get_config().MAX_ROWS} строк")
                else:
                    process_data(df)
                    st.success("CSV загружен!")
            except Exception as exc:
                st.error(f"Ошибка: {exc}")

    with col2:
        if st.button("Загрузить Google Sheets") and sheet_url:
            try:
                df = loader.load_google_sheets(sheet_url)
                process_data(df)
                st.success("Google Sheets загружен!")
            except Exception as exc:
                st.error(f"Ошибка: {exc}")

    if st.session_state.df is not None:
        df = st.session_state.df
        st.subheader("Превью данных")
        st.dataframe(df, use_container_width=True)

        is_valid, missing = loader.validate_schema(df)
        if is_valid:
            st.success("✅ Структура данных валидна")
        else:
            st.error(f"❌ Отсутствуют столбцы: {', '.join(missing)}")

        structure = loader.detect_structure(df)
        st.info(
            f"Строк: {structure['row_count']} | "
            f"Период: {structure.get('date_range', 'N/A')}"
        )


def render_dashboard_tab() -> None:
    """Таб дашборда KPI."""
    st.header("📊 Дашборд KPI")

    if st.session_state.kpis is None:
        st.warning("Загрузите данные на вкладке «Данные»")
        return

    kpis = st.session_state.kpis
    deltas = kpis.get("deltas", {})
    monthly = kpis.get("monthly", {})

    cols = st.columns(5)
    metrics = [
        ("CAC", "cac", " руб."),
        ("LTV", "ltv", " руб."),
        ("MRR", "mrr", " руб."),
        ("Churn", "churn", "%"),
        ("Conversion", "conversion", "%"),
    ]
    for col, (label, key, suffix) in zip(cols, metrics):
        delta = deltas.get(key)
        col.metric(
            label=f"{label}{suffix}",
            value=f"{kpis.get(key, 0):,.2f}",
            delta=f"{delta}%" if delta is not None else None,
        )

    if monthly.get("months"):
        fig_mrr = go.Figure()
        fig_mrr.add_trace(
            go.Scatter(
                x=monthly["months"],
                y=monthly["mrr"],
                mode="lines+markers",
                name="MRR",
                line=dict(color="#636EFA"),
            )
        )
        fig_mrr.update_layout(title="MRR по месяцам", xaxis_title="Месяц", yaxis_title="₽")
        st.plotly_chart(fig_mrr, use_container_width=True)

        fig_churn = go.Figure()
        fig_churn.add_trace(
            go.Bar(
                x=monthly["months"],
                y=monthly["churn"],
                name="Churn Rate",
                marker_color="#EF553B",
            )
        )
        fig_churn.update_layout(title="Churn Rate по месяцам", xaxis_title="Месяц", yaxis_title="%")
        st.plotly_chart(fig_churn, use_container_width=True)

        fig_cac_ltv = make_subplots(specs=[[{"secondary_y": True}]])
        fig_cac_ltv.add_trace(
            go.Scatter(x=monthly["months"], y=monthly["cac"], name="CAC"),
            secondary_y=False,
        )
        fig_cac_ltv.add_trace(
            go.Scatter(x=monthly["months"], y=monthly["ltv"], name="LTV"),
            secondary_y=True,
        )
        fig_cac_ltv.update_layout(title="CAC vs LTV")
        st.plotly_chart(fig_cac_ltv, use_container_width=True)

    anomalies = st.session_state.anomalies
    st.subheader("🔍 Аномалии")
    if anomalies:
        anomaly_df = pd.DataFrame(anomalies)
        st.dataframe(
            anomaly_df.style.apply(highlight_anomalies, axis=1),
            use_container_width=True,
        )
    else:
        st.info("Аномалий не обнаружено")


def highlight_anomalies(row: pd.Series) -> List[str]:
    """Подсветка строк аномалий."""
    return ["background-color: #ffcccc"] * len(row)


def render_ai_tab(db: ChatDatabase) -> None:
    """Таб AI-аналитика."""
    st.header("🤖 AI-аналитик")

    if not st.session_state.chat_history:
        st.session_state.chat_history = db.load_history()

    for msg in st.session_state.chat_history:
        icon = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=icon):
            st.markdown(msg["content"])

    if st.button("🗑️ Очистить историю"):
        db.clear_history()
        st.session_state.chat_history = []
        st.rerun()

    question = st.chat_input("Задайте вопрос о KPI...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        db.save_message("user", question)

        with st.chat_message("user", avatar="👤"):
            st.markdown(question)

        answer = get_ai_answer(question)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        db.save_message("assistant", answer)

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(answer)


def get_ai_answer(question: str) -> str:
    """Получает ответ AI-аналитика через RAG + LLM."""
    try:
        config = get_config()
        if not config.CLAUDE_API_KEY and config.LLM_PROVIDER == "claude":
            return "⚠️ CLAUDE_API_KEY не задан. Добавьте ключ в .env"

        rag = RAGEngine()
        context = rag.search(question)
        kpis = st.session_state.kpis or {}
        llm = LLMClient(provider=config.LLM_PROVIDER)
        return llm.ask(question, context, kpis)
    except Exception as exc:
        logger.error("Ошибка AI-ответа: %s", exc)
        return f"Ошибка: {exc}"


def render_settings_tab(db: ChatDatabase) -> None:
    """Таб настроек и интеграций."""
    st.header("⚙️ Настройки")
    config = get_config()

    st.subheader("Статус API")
    col1, col2 = st.columns(2)
    with col1:
        claude_status = "✅ Подключён" if config.CLAUDE_API_KEY else "❌ Не настроен"
        st.write(f"**Claude:** {claude_status}")
    with col2:
        tg_status = (
            "✅ Подключён"
            if config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID
            else "❌ Не настроен"
        )
        st.write(f"**Telegram:** {tg_status}")

    st.write(f"**LLM-провайдер:** {config.LLM_PROVIDER}")
    st.write(f"**ChromaDB:** {config.CHROMA_DB_PATH}")
    st.write(f"**SQLite:** {config.SQLITE_DB_PATH}")

    if st.button("📨 Отправить дайджест сейчас"):
        send_digest_now()

    if st.button("🔄 Переиндексировать данные"):
        reindex_data()


def send_digest_now() -> None:
    """Отправляет дайджест в Telegram."""
    try:
        if st.session_state.kpis is None:
            st.warning("Нет данных для дайджеста")
            return

        llm = LLMClient()
        digest = llm.generate_digest(
            st.session_state.kpis, st.session_state.anomalies
        )
        bot = TelegramDigestBot()
        if bot.send_digest(digest):
            st.success("Дайджест отправлен!")
        else:
            st.error("Не удалось отправить. Проверьте TELEGRAM_TOKEN и TELEGRAM_CHAT_ID")
    except Exception as exc:
        logger.error("Ошибка отправки дайджеста: %s", exc)
        st.error(f"Ошибка: {exc}")


def reindex_data() -> None:
    """Переиндексирует данные в ChromaDB."""
    try:
        if st.session_state.df is None:
            st.warning("Нет данных для индексации")
            return
        rag = RAGEngine()
        rag.index_data(st.session_state.df, st.session_state.kpis)
        st.success("Данные переиндексированы!")
    except Exception as exc:
        logger.error("Ошибка переиндексации: %s", exc)
        st.error(f"Ошибка: {exc}")


def main() -> None:
    """Точка входа Streamlit-приложения."""
    st.set_page_config(
        page_title="KPI Pulse",
        page_icon="📈",
        layout="wide",
    )
    st.title("📈 KPI Pulse — AI-аналитика бизнес-метрик")

    init_session_state()
    db = ChatDatabase()
    show_terms_modal(db)
    load_sample_data()

    tab_data, tab_dashboard, tab_ai, tab_settings = st.tabs(
        ["Данные", "Дашборд KPI", "AI-аналитик", "Настройки"]
    )

    with tab_data:
        render_data_tab()
    with tab_dashboard:
        render_dashboard_tab()
    with tab_ai:
        render_ai_tab(db)
    with tab_settings:
        render_settings_tab(db)


if __name__ == "__main__":
    main()
