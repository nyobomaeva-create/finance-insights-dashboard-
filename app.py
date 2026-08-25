"""Streamlit interface for the Finance Insights Dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from finance_insights.analytics import (
    calculate_kpis,
    category_expenses,
    detect_anomalies,
    largest_transactions,
    monthly_summary,
)
from finance_insights.insights import generate_insights
from finance_insights.validation import clean_transactions

SAMPLE_PATH = Path(__file__).parent / "data" / "sample_transactions.csv"


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    """Load and validate the bundled demonstration transactions."""
    return clean_transactions(pd.read_csv(SAMPLE_PATH))


def money(value: float) -> str:
    """Format a numeric KPI as US-dollar demonstration data."""
    return f"${value:,.2f}"


def report_csv(frame: pd.DataFrame) -> bytes:
    """Serialize cleaned transactions with stable ISO dates."""
    report = frame.copy()
    report["date"] = report["date"].dt.strftime("%Y-%m-%d")
    return report.to_csv(index=False).encode("utf-8")


st.set_page_config(page_title="Finance Insights Dashboard", page_icon="📊", layout="wide")
st.title("Finance Insights Dashboard")
st.caption(
    "Turn a transaction CSV into clear KPIs, trends, category summaries, and explainable "
    "anomaly flags. Demonstration only — not financial advice."
)

with st.sidebar:
    st.header("Data source")
    uploaded_file = st.file_uploader("Upload transaction CSV", type="csv")
    st.markdown("Required columns: `date`, `description`, `category`, `amount`.")
    st.download_button(
        "Download example CSV",
        data=SAMPLE_PATH.read_bytes(),
        file_name="sample_transactions.csv",
        mime="text/csv",
        width="stretch",
    )

try:
    if uploaded_file is None:
        transactions = load_sample_data()
        st.info("Showing bundled sample data. Upload a CSV from the sidebar to analyze your own file.")
    else:
        transactions = clean_transactions(pd.read_csv(uploaded_file))
        st.success(f"Loaded {len(transactions)} transactions from {uploaded_file.name}.")
except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
    st.error(f"Could not process this CSV: {exc}")
    st.stop()

kpis = calculate_kpis(transactions)
categories = category_expenses(transactions)
monthly = monthly_summary(transactions)
anomalies = detect_anomalies(transactions)

st.header("Overview")
income_col, expense_col, balance_col, rate_col = st.columns(4)
income_col.metric("Income", money(kpis["income"]))
expense_col.metric("Expenses", money(kpis["expenses"]))
balance_col.metric("Balance", money(kpis["balance"]))
rate_col.metric("Savings rate", f"{kpis['savings_rate']:.1f}%")

st.subheader("Automated insights")
for insight in generate_insights(transactions):
    st.markdown(f"- {insight}")

trend_col, category_col = st.columns(2)
with trend_col:
    st.subheader("Monthly trends")
    trend_long = monthly.melt(
        id_vars="month", value_vars=["income", "expenses", "balance"], var_name="metric"
    )
    trend_chart = px.line(
        trend_long,
        x="month",
        y="value",
        color="metric",
        markers=True,
        labels={"value": "Amount ($)", "month": "Month", "metric": "Metric"},
    )
    st.plotly_chart(trend_chart, width="stretch")

with category_col:
    st.subheader("Expense categories")
    category_chart = px.bar(
        categories,
        x="expenses",
        y="category",
        orientation="h",
        labels={"expenses": "Expenses ($)", "category": "Category"},
    )
    category_chart.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(category_chart, width="stretch")

st.subheader("Largest transactions")
largest = largest_transactions(transactions, limit=8).copy()
largest["date"] = largest["date"].dt.strftime("%Y-%m-%d")
st.dataframe(largest, hide_index=True, width="stretch")

st.subheader("Unusually large transactions")
st.caption("Flagged when the absolute amount exceeds Q3 + 1.5 × IQR.")
if anomalies.empty:
    st.success("No unusually large transactions were detected.")
else:
    anomaly_view = anomalies.copy()
    anomaly_view["date"] = anomaly_view["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(anomaly_view, hide_index=True, width="stretch")

st.download_button(
    "Download cleaned report",
    data=report_csv(transactions),
    file_name="cleaned_transactions.csv",
    mime="text/csv",
    type="primary",
)
