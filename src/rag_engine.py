"""
Модуль RAG-движка на базе ChromaDB.
Индексация KPI-данных и семантический поиск контекста.
"""

import logging
from typing import Any, Dict, List

import chromadb
import pandas as pd

from config import CHROMA_COLLECTION_NAME, get_config

logger = logging.getLogger(__name__)


class RAGEngine:
    """Векторное хранилище для контекстного поиска по KPI-данным."""

    def __init__(self) -> None:
        try:
            self.config = get_config()
            self.client = chromadb.PersistentClient(
                path=self.config.CHROMA_DB_PATH
            )
            self.collection = self.client.get_or_create_collection(
                name=CHROMA_COLLECTION_NAME,
                metadata={"description": "KPI business data index"},
            )
            logger.info("ChromaDB инициализирован: %s", self.config.CHROMA_DB_PATH)
        except Exception as exc:
            logger.error("Ошибка инициализации ChromaDB: %s", exc)
            raise RuntimeError(f"Не удалось инициализировать ChromaDB: {exc}") from exc

    def index_data(self, df: pd.DataFrame, kpis: Dict[str, Any]) -> None:
        """Индексирует строки датафрейма и KPI в ChromaDB."""
        try:
            if df is None or df.empty:
                logger.warning("Пустой датафрейм — индексация пропущена")
                return

            self.clear_index()
            documents: List[str] = []
            metadatas: List[Dict[str, str]] = []
            ids: List[str] = []

            for idx, row in df.iterrows():
                doc_text = self._row_to_document(row, kpis)
                documents.append(doc_text)
                metadatas.append(
                    {"month": str(row["month"]), "metric": "monthly_data"}
                )
                ids.append(f"row_{idx}")

            kpi_doc = self._kpis_to_document(kpis)
            documents.append(kpi_doc)
            metadatas.append({"month": kpis.get("month", "latest"), "metric": "kpi_summary"})
            ids.append("kpi_summary")

            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info("Проиндексировано %d документов", len(documents))
        except Exception as exc:
            logger.error("Ошибка индексации данных: %s", exc)
            raise RuntimeError(f"Не удалось проиндексировать данные: {exc}") from exc

    def search(self, query: str, n_results: int = 5) -> List[str]:
        """Семантический поиск релевантного контекста по запросу."""
        try:
            if not query or not query.strip():
                return []

            count = self.collection.count()
            if count == 0:
                logger.warning("Индекс пуст — поиск невозможен")
                return []

            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, count),
            )
            documents = results.get("documents", [[]])[0]
            logger.info("Найдено %d документов по запросу", len(documents))
            return documents
        except Exception as exc:
            logger.error("Ошибка поиска в ChromaDB: %s", exc)
            return []

    def clear_index(self) -> None:
        """Очищает коллекцию при загрузке новых данных."""
        try:
            existing = self.collection.get()
            if existing and existing.get("ids"):
                self.collection.delete(ids=existing["ids"])
                logger.info("Индекс очищен: удалено %d документов", len(existing["ids"]))
        except Exception as exc:
            logger.error("Ошибка очистки индекса: %s", exc)
            raise RuntimeError(f"Не удалось очистить индекс: {exc}") from exc

    def _row_to_document(self, row: pd.Series, kpis: Dict[str, Any]) -> str:
        """Преобразует строку датафрейма в текстовый документ."""
        return (
            f"Месяц: {row['month']}. "
            f"Новые клиенты: {row['new_customers']}, "
            f"Потерянные клиенты: {row['lost_customers']}, "
            f"Выручка: {row['revenue']} руб., "
            f"Маркетинговые расходы: {row['marketing_spend']} руб., "
            f"Всего клиентов: {row['total_customers']}, "
            f"Закрытые сделки: {row['deals_closed']} из {row['deals_total']}."
        )

    def _kpis_to_document(self, kpis: Dict[str, Any]) -> str:
        """Преобразует сводку KPI в текстовый документ."""
        return (
            f"Сводка KPI за {kpis.get('month', 'N/A')}: "
            f"CAC = {kpis.get('cac', 0)} руб., "
            f"LTV = {kpis.get('ltv', 0)} руб., "
            f"MRR = {kpis.get('mrr', 0)} руб., "
            f"Churn Rate = {kpis.get('churn', 0)}%, "
            f"Conversion = {kpis.get('conversion', 0)}%."
        )
