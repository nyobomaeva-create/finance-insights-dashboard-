"""Deterministic financial summaries for cleaned transactions."""

import pandas as pd


def calculate_kpis(frame: pd.DataFrame) -> dict[str, float]:
    """Return total income, expenses, balance, and savings rate."""
    income = float(frame.loc[frame["amount"] > 0, "amount"].sum())
    expenses = float(-frame.loc[frame["amount"] < 0, "amount"].sum())
    balance = income - expenses
    savings_rate = balance / income * 100 if income else 0.0
    return {
        "income": income,
        "expenses": expenses,
        "balance": balance,
        "savings_rate": round(savings_rate, 2),
    }


def category_expenses(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate expense magnitude by category, largest first."""
    expenses = frame.loc[frame["amount"] < 0, ["category", "amount"]].copy()
    expenses["expenses"] = -expenses["amount"]
    return (
        expenses.groupby("category", as_index=False)["expenses"]
        .sum()
        .sort_values("expenses", ascending=False, kind="stable")
        .reset_index(drop=True)
    )


def monthly_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate income, expenses, and balance by calendar month."""
    working = frame.assign(month=frame["date"].dt.to_period("M").astype(str))
    rows = []
    for month, group in working.groupby("month", sort=True):
        kpis = calculate_kpis(group)
        rows.append({"month": month, **{key: kpis[key] for key in ("income", "expenses", "balance")}})
    return pd.DataFrame(rows, columns=["month", "income", "expenses", "balance"])


def largest_transactions(frame: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """Return the transactions with the largest absolute amounts."""
    ranked = frame.assign(_magnitude=frame["amount"].abs()).sort_values(
        "_magnitude", ascending=False, kind="stable"
    )
    return ranked.drop(columns="_magnitude").head(limit).reset_index(drop=True)


def detect_anomalies(frame: pd.DataFrame) -> pd.DataFrame:
    """Flag amounts above the upper 1.5×IQR fence of absolute values."""
    magnitude = frame["amount"].abs()
    q1, q3 = magnitude.quantile([0.25, 0.75])
    threshold = float(q3 + 1.5 * (q3 - q1))
    result = frame.loc[magnitude > threshold].copy()
    result["anomaly_threshold"] = threshold
    return result.sort_values("amount", key=lambda values: values.abs(), ascending=False).reset_index(
        drop=True
    )
