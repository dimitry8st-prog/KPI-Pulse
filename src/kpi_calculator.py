"""
Модуль расчёта ключевых KPI: CAC, LTV, MRR, Churn, Conversion.
Обнаружение аномалий методом IQR.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from config import DEFAULT_LIFESPAN_MONTHS

logger = logging.getLogger(__name__)

METRIC_COLUMNS = [
    "revenue",
    "marketing_spend",
    "new_customers",
    "lost_customers",
    "total_customers",
    "deals_closed",
    "deals_total",
]


class KPICalculator:
    """Калькулятор бизнес-KPI на основе датафрейма."""

    def calculate_cac(
        self, marketing_spend: float, new_customers: float
    ) -> float:
        """CAC = marketing_spend / new_customers."""
        if new_customers is None or marketing_spend is None:
            raise ValueError("marketing_spend и new_customers не могут быть None")
        if new_customers == 0:
            raise ZeroDivisionError("new_customers равен нулю — CAC не определён")
        return round(marketing_spend / new_customers, 2)

    def calculate_ltv(
        self,
        avg_revenue_per_customer: float,
        avg_customer_lifespan_months: float,
    ) -> float:
        """LTV = ARPU × avg_lifespan."""
        if avg_revenue_per_customer is None or avg_customer_lifespan_months is None:
            raise ValueError("Параметры LTV не могут быть None")
        return round(avg_revenue_per_customer * avg_customer_lifespan_months, 2)

    def calculate_mrr(self, monthly_revenue: pd.Series) -> pd.Series:
        """MRR за каждый месяц из серии выручки."""
        if monthly_revenue is None:
            raise ValueError("monthly_revenue не может быть None")
        return monthly_revenue.astype(float).round(2)

    def calculate_churn(
        self, lost_customers: float, total_customers_start: float
    ) -> float:
        """Churn Rate = lost / total × 100."""
        if lost_customers is None or total_customers_start is None:
            raise ValueError("Параметры churn не могут быть None")
        if total_customers_start == 0:
            raise ZeroDivisionError(
                "total_customers_start равен нулю — Churn Rate не определён"
            )
        return round((lost_customers / total_customers_start) * 100, 2)

    def calculate_conversion(
        self, deals_closed: float, deals_total: float
    ) -> float:
        """Conversion = closed / total × 100."""
        if deals_closed is None or deals_total is None:
            raise ValueError("Параметры conversion не могут быть None")
        if deals_total == 0:
            raise ZeroDivisionError("deals_total равен нулю — Conversion не определён")
        return round((deals_closed / deals_total) * 100, 2)

    def calculate_all(
        self, df: pd.DataFrame, target_month: Optional[str] = None
    ) -> Dict[str, Any]:
        """Рассчитывает все KPI и дельты к предыдущему периоду."""
        try:
            if df is None or df.empty:
                raise ValueError("Датафрейм пуст — невозможно рассчитать KPI")

            df_sorted = df.sort_values("month").reset_index(drop=True)
            latest, previous = self._resolve_periods(df_sorted, target_month)

            kpis = self._compute_period_kpis(df_sorted, latest)
            if previous is not None:
                prev_kpis = self._compute_period_kpis(df_sorted, previous)
                kpis["deltas"] = self._compute_deltas(kpis, prev_kpis)
            else:
                kpis["deltas"] = {}

            kpis["monthly"] = self._compute_monthly_series(df_sorted)
            logger.info("KPI рассчитаны для периода: %s", latest.get("month"))
            return kpis
        except Exception as exc:
            logger.error("Ошибка расчёта KPI: %s", exc)
            raise

    def filter_anomalies_for_month(
        self, anomalies: List[Dict[str, Any]], target_month: str
    ) -> List[Dict[str, Any]]:
        """Оставляет аномалии только за указанный месяц."""
        normalized = self._normalize_month(target_month)
        return [
            item
            for item in anomalies
            if self._normalize_month(str(item.get("month", ""))) == normalized
        ]

    def detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Находит выбросы методом IQR по числовым метрикам."""
        anomalies: List[Dict[str, Any]] = []
        try:
            if df is None or df.empty:
                return anomalies

            for metric in METRIC_COLUMNS:
                if metric not in df.columns:
                    continue
                anomalies.extend(self._find_iqr_outliers(df, metric))

            logger.info("Обнаружено аномалий: %d", len(anomalies))
            return anomalies
        except Exception as exc:
            logger.error("Ошибка обнаружения аномалий: %s", exc)
            return anomalies

    def _compute_period_kpis(
        self, df: pd.DataFrame, row: pd.Series
    ) -> Dict[str, Any]:
        """Рассчитывает KPI для одного периода."""
        total_customers = float(row["total_customers"])
        new_customers = float(row["new_customers"])
        revenue = float(row["revenue"])
        marketing_spend = float(row["marketing_spend"])

        arpu = revenue / total_customers if total_customers > 0 else 0.0
        cac = self._safe_cac(marketing_spend, new_customers)
        ltv = self.calculate_ltv(arpu, DEFAULT_LIFESPAN_MONTHS)
        churn = self._safe_churn(
            float(row["lost_customers"]),
            total_customers - new_customers + float(row["lost_customers"]),
        )
        conversion = self._safe_conversion(
            float(row["deals_closed"]), float(row["deals_total"])
        )
        mrr = revenue

        return {
            "month": str(row["month"]),
            "cac": cac,
            "ltv": ltv,
            "mrr": mrr,
            "churn": churn,
            "conversion": conversion,
            "arpu": round(arpu, 2),
        }

    def _compute_deltas(
        self, current: Dict[str, Any], previous: Dict[str, Any]
    ) -> Dict[str, Optional[float]]:
        """Вычисляет процентное изменение KPI к предыдущему периоду."""
        deltas: Dict[str, Optional[float]] = {}
        for key in ["cac", "ltv", "mrr", "churn", "conversion"]:
            curr_val = current.get(key)
            prev_val = previous.get(key)
            deltas[key] = self._percent_change(curr_val, prev_val)
        return deltas

    def _compute_monthly_series(self, df: pd.DataFrame) -> Dict[str, List[Any]]:
        """Формирует помесячные серии для графиков."""
        months = df["month"].astype(str).tolist()
        mrr_series = self.calculate_mrr(df["revenue"])
        churn_series = []
        cac_series = []
        ltv_series = []

        for _, row in df.iterrows():
            total = float(row["total_customers"])
            new_c = float(row["new_customers"])
            lost = float(row["lost_customers"])
            start_total = total - new_c + lost
            churn_series.append(self._safe_churn(lost, start_total))
            cac_series.append(
                self._safe_cac(float(row["marketing_spend"]), new_c)
            )
            arpu = float(row["revenue"]) / total if total > 0 else 0.0
            ltv_series.append(self.calculate_ltv(arpu, DEFAULT_LIFESPAN_MONTHS))

        return {
            "months": months,
            "mrr": mrr_series.tolist(),
            "churn": churn_series,
            "cac": cac_series,
            "ltv": ltv_series,
        }

    def _find_iqr_outliers(
        self, df: pd.DataFrame, metric: str
    ) -> List[Dict[str, Any]]:
        """Находит выбросы по одной метрике методом IQR."""
        values = df[metric].astype(float)
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers: List[Dict[str, Any]] = []
        for idx, val in values.items():
            if val < lower or val > upper:
                direction = "выше нормы" if val > upper else "ниже нормы"
                outliers.append(
                    {
                        "metric": metric,
                        "month": str(df.loc[idx, "month"]),
                        "value": round(float(val), 2),
                        "reason": f"Значение {direction} (IQR: {round(lower, 2)}–{round(upper, 2)})",
                    }
                )
        return outliers

    def _safe_cac(self, marketing_spend: float, new_customers: float) -> float:
        """Безопасный расчёт CAC без исключений."""
        try:
            return self.calculate_cac(marketing_spend, new_customers)
        except (ZeroDivisionError, ValueError):
            return 0.0

    def _safe_churn(
        self, lost_customers: float, total_start: float
    ) -> float:
        """Безопасный расчёт Churn без исключений."""
        try:
            return self.calculate_churn(lost_customers, total_start)
        except (ZeroDivisionError, ValueError):
            return 0.0

    def _safe_conversion(
        self, deals_closed: float, deals_total: float
    ) -> float:
        """Безопасный расчёт Conversion без исключений."""
        try:
            return self.calculate_conversion(deals_closed, deals_total)
        except (ZeroDivisionError, ValueError):
            return 0.0

    def _percent_change(
        self, current: Optional[float], previous: Optional[float]
    ) -> Optional[float]:
        """Процентное изменение между двумя значениями."""
        if current is None or previous is None or previous == 0:
            return None
        return round(((current - previous) / abs(previous)) * 100, 2)

    def _resolve_periods(
        self, df_sorted: pd.DataFrame, target_month: Optional[str]
    ) -> tuple[pd.Series, Optional[pd.Series]]:
        """Возвращает целевой и предыдущий периоды."""
        if target_month is None:
            latest = df_sorted.iloc[-1]
            previous = df_sorted.iloc[-2] if len(df_sorted) > 1 else None
            return latest, previous

        normalized = self._normalize_month(target_month)
        month_series = df_sorted["month"].astype(str).apply(self._normalize_month)
        matches = df_sorted[month_series == normalized]
        if matches.empty:
            raise ValueError(f"Месяц {target_month} не найден в данных")

        latest = matches.iloc[-1]
        pos = df_sorted.index.get_loc(latest.name)
        previous = df_sorted.iloc[pos - 1] if pos > 0 else None
        return latest, previous

    def _normalize_month(self, month: str) -> str:
        """Приводит месяц к формату YYYY-MM."""
        return str(month).strip()[:7]
