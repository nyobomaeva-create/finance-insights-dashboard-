"""Explainable payment-operations KPIs for synthetic or approved CSV exports.

This MVP is an analytics-only tool: it does not route or block payments.
"""

import pandas as pd

REQUIRED_COLUMNS = (
    "transaction_id", "date", "provider", "bank", "country", "status",
    "amount", "currency", "decline_reason",
)
VALID_STATUSES = {"approved", "failed", "pending"}
BREAKDOWN_COLUMNS = {"provider", "bank", "country"}


def validate_payments(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate a payment export, returning a normalized, date-sorted copy."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    if frame.empty:
        raise ValueError("The payment CSV is empty.")

    cleaned = frame.loc[:, REQUIRED_COLUMNS].copy()
    for column in ("transaction_id", "provider", "bank", "country", "currency"):
        if cleaned[column].isna().any():
            raise ValueError(f"'{column}' contains missing values.")
        cleaned[column] = cleaned[column].astype(str).str.strip()
        if cleaned[column].eq("").any():
            raise ValueError(f"'{column}' contains blank values.")

    if cleaned["transaction_id"].duplicated().any():
        raise ValueError("Duplicate transaction_id values were found.")

    cleaned["date"] = pd.to_datetime(cleaned["date"], format="%Y-%m-%d", errors="coerce")
    if cleaned["date"].isna().any():
        raise ValueError("Invalid date. Expected YYYY-MM-DD.")

    amounts = pd.to_numeric(cleaned["amount"], errors="coerce")
    if amounts.isna().any() or not amounts.ge(0).all():
        raise ValueError("Amounts must be non-negative finite numbers.")
    # Avoid silently accepting infinities as transaction values.
    import numpy as np
    if not np.isfinite(amounts).all():
        raise ValueError("Amounts must be non-negative finite numbers.")
    cleaned["amount"] = amounts.astype(float)

    if cleaned["status"].isna().any():
        raise ValueError("Missing payment status.")
    cleaned["status"] = cleaned["status"].astype(str).str.strip().str.lower()
    if not cleaned["status"].isin(VALID_STATUSES).all():
        raise ValueError("Status must be approved, failed, or pending.")

    cleaned["decline_reason"] = (
        cleaned["decline_reason"].fillna("").astype(str).str.strip()
    )
    return cleaned.sort_values("date", kind="stable").reset_index(drop=True)


def payment_kpis(frame: pd.DataFrame) -> dict[str, float | int | None]:
    """Calculate counts and approval rate among resolved transactions only."""
    approved = int(frame["status"].eq("approved").sum())
    failed = int(frame["status"].eq("failed").sum())
    pending = int(frame["status"].eq("pending").sum())
    resolved = approved + failed
    return {
        "total": int(len(frame)), "approved": approved, "failed": failed,
        "pending": pending, "resolved": resolved,
        "approval_rate_pct": round(100 * approved / resolved, 2) if resolved else None,
    }


def approval_by(frame: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Break down payment outcomes by provider, bank, or country."""
    if dimension not in BREAKDOWN_COLUMNS:
        raise ValueError(f"Unsupported breakdown: {dimension}")
    grouped = (
        frame.groupby([dimension, "status"]).size()
        .unstack(fill_value=0)
        .reindex(columns=["approved", "failed", "pending"], fill_value=0)
        .reset_index()
    )
    grouped["resolved"] = grouped["approved"] + grouped["failed"]
    grouped["approval_rate_pct"] = (
        100 * grouped["approved"] / grouped["resolved"].where(grouped["resolved"].ne(0))
    ).round(2)
    return grouped.sort_values("resolved", ascending=False, kind="stable").reset_index(drop=True)


def failure_reasons(frame: pd.DataFrame) -> pd.DataFrame:
    """Count reasons for failed payments, treating blank reasons as unspecified."""
    failures = frame.loc[frame["status"].eq("failed"), "decline_reason"].copy()
    failures = failures.replace("", "Unspecified")
    counts = failures.value_counts().rename_axis("reason").reset_index(name="count")
    return counts
