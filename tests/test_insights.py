import pandas as pd

from finance_insights.insights import generate_insights
from finance_insights.validation import clean_transactions


def test_generate_insights_summarizes_business_signals():
    frame = clean_transactions(
        pd.DataFrame(
            {
                "date": ["2026-01-01", "2026-01-05", "2026-02-01", "2026-02-07", "2026-02-09"],
                "description": ["Sale", "Rent", "Sale", "Rent", "Large equipment"],
                "category": ["Income", "Rent", "Income", "Rent", "Equipment"],
                "amount": [1000, -200, 1200, -300, -5000],
            }
        )
    )
    insights = generate_insights(frame)
    assert len(insights) == 4
    assert "Equipment" in insights[0]
    assert "increased" in insights[1]
    assert "negative" in insights[2]
    assert "unusually large" in insights[3]


def test_generate_insights_handles_single_month_without_change_claim():
    frame = clean_transactions(
        pd.DataFrame(
            {
                "date": ["2026-01-01", "2026-01-05"],
                "description": ["Sale", "Rent"],
                "category": ["Income", "Rent"],
                "amount": [1000, -200],
            }
        )
    )
    assert "one month" in generate_insights(frame)[1]
