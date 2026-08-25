"""Validation and cleaning for transaction data."""

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ("date", "description", "category", "amount")


def clean_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate, normalize, and date-sort a transaction frame."""
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    if frame.empty:
        raise ValueError("CSV must contain at least one transaction.")

    cleaned = frame.loc[:, REQUIRED_COLUMNS].copy()
    parsed_dates = pd.to_datetime(cleaned["date"], format="%Y-%m-%d", errors="coerce")
    if parsed_dates.isna().any():
        raise ValueError("Invalid date found. Use YYYY-MM-DD values.")
    parsed_amounts = pd.to_numeric(cleaned["amount"], errors="coerce")
    if parsed_amounts.isna().any():
        raise ValueError("Invalid amount found. Amounts must be numeric.")
    if not np.isfinite(parsed_amounts).all():
        raise ValueError("Invalid amount found. Amounts must be finite numbers.")

    for column in ("description", "category"):
        if cleaned[column].isna().any():
            raise ValueError(f"Column '{column}' cannot contain empty values.")
        cleaned[column] = cleaned[column].astype(str).str.strip()
        if cleaned[column].eq("").any():
            raise ValueError(f"Column '{column}' cannot contain empty values.")
    cleaned["date"] = parsed_dates
    cleaned["amount"] = parsed_amounts.astype(float)
    return cleaned.sort_values("date", kind="stable").reset_index(drop=True)
