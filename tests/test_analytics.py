import pandas as pd
import pytest

from finance_insights.analytics import (
    calculate_kpis,
    category_expenses,
    detect_anomalies,
    largest_transactions,
    monthly_summary,
)
from finance_insights.validation import clean_transactions


def transactions():
    return clean_transactions(
        pd.DataFrame(
            {
                "date": ["2026-01-01", "2026-01-05", "2026-02-01", "2026-02-07"],
                "description": ["Sale", "Rent", "Sale", "Ads"],
                "category": ["Income", "Rent", "Income", "Marketing"],
                "amount": [1000, -400, 1200, -300],
            }
        )
    )


def test_calculate_kpis_returns_business_totals():
    result = calculate_kpis(transactions())
    assert result == {
        "income": 2200.0,
        "expenses": 700.0,
        "balance": 1500.0,
        "savings_rate": pytest.approx(68.18, abs=0.01),
    }


def test_category_expenses_aggregates_negative_amounts():
    result = category_expenses(transactions())
    assert result.to_dict("records") == [
        {"category": "Rent", "expenses": 400.0},
        {"category": "Marketing", "expenses": 300.0},
    ]


def test_monthly_summary_calculates_income_expenses_and_balance():
    result = monthly_summary(transactions())
    assert result.to_dict("records") == [
        {"month": "2026-01", "income": 1000.0, "expenses": 400.0, "balance": 600.0},
        {"month": "2026-02", "income": 1200.0, "expenses": 300.0, "balance": 900.0},
    ]


def test_largest_transactions_ranks_by_absolute_amount():
    result = largest_transactions(transactions(), limit=2)
    assert result["description"].tolist() == ["Sale", "Sale"]
    assert result["amount"].tolist() == [1200.0, 1000.0]


def test_detect_anomalies_uses_upper_iqr_fence_on_absolute_amounts():
    frame = clean_transactions(
        pd.DataFrame(
            {
                "date": ["2026-01-01"] * 5,
                "description": ["A", "B", "C", "D", "Large"],
                "category": ["Other"] * 5,
                "amount": [-10, -12, -11, -9, -100],
            }
        )
    )
    result = detect_anomalies(frame)
    assert result["description"].tolist() == ["Large"]
    assert result["anomaly_threshold"].iloc[0] == pytest.approx(15.0)
