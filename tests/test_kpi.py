"""
Юнит-тесты для модуля kpi_calculator.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kpi_calculator import KPICalculator


@pytest.fixture
def calculator() -> KPICalculator:
    """Фикстура калькулятора KPI."""
    return KPICalculator()


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Тестовый датафрейм с двумя месяцами."""
    return pd.DataFrame(
        {
            "month": ["2024-01", "2024-02"],
            "new_customers": [50, 60],
            "lost_customers": [10, 12],
            "revenue": [100000, 120000],
            "marketing_spend": [10000, 12000],
            "total_customers": [200, 250],
            "deals_closed": [30, 35],
            "deals_total": [100, 110],
        }
    )


class TestCalculateCac:
    """Тесты расчёта CAC."""

    @pytest.mark.parametrize(
        "marketing_spend,new_customers,expected",
        [
            (10000, 50, 200.0),
            (15000, 100, 150.0),
            (0, 50, 0.0),
        ],
    )
    def test_valid_cac(
        self,
        calculator: KPICalculator,
        marketing_spend: float,
        new_customers: float,
        expected: float,
    ) -> None:
        result = calculator.calculate_cac(marketing_spend, new_customers)
        assert result == expected

    def test_zero_customers_raises(self, calculator: KPICalculator) -> None:
        with pytest.raises(ZeroDivisionError):
            calculator.calculate_cac(10000, 0)

    def test_none_raises(self, calculator: KPICalculator) -> None:
        with pytest.raises(ValueError):
            calculator.calculate_cac(None, 50)


class TestCalculateLtv:
    """Тесты расчёта LTV."""

    @pytest.mark.parametrize(
        "arpu,lifespan,expected",
        [
            (500, 24, 12000.0),
            (1000, 12, 12000.0),
            (0, 24, 0.0),
        ],
    )
    def test_valid_ltv(
        self,
        calculator: KPICalculator,
        arpu: float,
        lifespan: float,
        expected: float,
    ) -> None:
        result = calculator.calculate_ltv(arpu, lifespan)
        assert result == expected

    def test_none_raises(self, calculator: KPICalculator) -> None:
        with pytest.raises(ValueError):
            calculator.calculate_ltv(None, 24)


class TestCalculateMrr:
    """Тесты расчёта MRR."""

    def test_valid_mrr(self, calculator: KPICalculator) -> None:
        revenue = pd.Series([100000, 120000, 115000])
        result = calculator.calculate_mrr(revenue)
        assert list(result) == [100000.0, 120000.0, 115000.0]

    def test_none_raises(self, calculator: KPICalculator) -> None:
        with pytest.raises(ValueError):
            calculator.calculate_mrr(None)


class TestCalculateChurn:
    """Тесты расчёта Churn Rate."""

    @pytest.mark.parametrize(
        "lost,total,expected",
        [
            (10, 200, 5.0),
            (50, 100, 50.0),
            (0, 200, 0.0),
            (100, 100, 100.0),
        ],
    )
    def test_valid_churn(
        self,
        calculator: KPICalculator,
        lost: float,
        total: float,
        expected: float,
    ) -> None:
        result = calculator.calculate_churn(lost, total)
        assert result == expected

    def test_zero_total_raises(self, calculator: KPICalculator) -> None:
        with pytest.raises(ZeroDivisionError):
            calculator.calculate_churn(10, 0)


class TestCalculateConversion:
    """Тесты расчёта Conversion."""

    @pytest.mark.parametrize(
        "closed,total,expected",
        [
            (30, 100, 30.0),
            (50, 50, 100.0),
            (0, 100, 0.0),
        ],
    )
    def test_valid_conversion(
        self,
        calculator: KPICalculator,
        closed: float,
        total: float,
        expected: float,
    ) -> None:
        result = calculator.calculate_conversion(closed, total)
        assert result == expected

    def test_zero_total_raises(self, calculator: KPICalculator) -> None:
        with pytest.raises(ZeroDivisionError):
            calculator.calculate_conversion(30, 0)


class TestCalculateAll:
    """Тесты комплексного расчёта KPI."""

    def test_calculate_all_returns_kpis(
        self, calculator: KPICalculator, sample_df: pd.DataFrame
    ) -> None:
        result = calculator.calculate_all(sample_df)
        assert "cac" in result
        assert "ltv" in result
        assert "mrr" in result
        assert "churn" in result
        assert "conversion" in result
        assert "deltas" in result
        assert "monthly" in result

    def test_empty_df_raises(self, calculator: KPICalculator) -> None:
        with pytest.raises(ValueError):
            calculator.calculate_all(pd.DataFrame())


class TestDetectAnomalies:
    """Тесты обнаружения аномалий."""

    def test_detect_anomalies_returns_list(
        self, calculator: KPICalculator, sample_df: pd.DataFrame
    ) -> None:
        result = calculator.detect_anomalies(sample_df)
        assert isinstance(result, list)

    def test_empty_df_returns_empty(
        self, calculator: KPICalculator
    ) -> None:
        result = calculator.detect_anomalies(pd.DataFrame())
        assert result == []
