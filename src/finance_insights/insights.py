"""Plain-language observations derived from transaction summaries."""

import pandas as pd

from finance_insights.analytics import (
    calculate_kpis,
    category_expenses,
    detect_anomalies,
    monthly_summary,
)


def generate_insights(frame: pd.DataFrame) -> list[str]:
    """Return four factual business observations without financial advice."""
    categories = category_expenses(frame)
    if categories.empty:
        category_note = "No expense categories are present in this dataset."
    else:
        top = categories.iloc[0]
        category_note = f"{top['category']} is the largest expense category at ${top['expenses']:,.2f}."

    months = monthly_summary(frame)
    if len(months) < 2:
        trend_note = "The dataset covers only one month, so no month-over-month comparison is shown."
    else:
        previous, latest = months.iloc[-2], months.iloc[-1]
        difference = float(latest["expenses"] - previous["expenses"])
        direction = "increased" if difference > 0 else "decreased" if difference < 0 else "were unchanged"
        trend_note = (
            f"Expenses {direction} by ${abs(difference):,.2f} in {latest['month']} compared with "
            f"{previous['month']}."
        )

    kpis = calculate_kpis(frame)
    if kpis["balance"] >= 0:
        balance_note = (
            f"The period ended with a positive balance of ${kpis['balance']:,.2f} "
            f"and a {kpis['savings_rate']:.1f}% savings rate."
        )
    else:
        balance_note = f"The period ended with a negative balance of ${abs(kpis['balance']):,.2f}."

    anomaly_count = len(detect_anomalies(frame))
    anomaly_note = (
        f"{anomaly_count} unusually large transaction{'s were' if anomaly_count != 1 else ' was'} "
        "flagged by the IQR rule."
    )
    return [category_note, trend_note, balance_note, anomaly_note]
