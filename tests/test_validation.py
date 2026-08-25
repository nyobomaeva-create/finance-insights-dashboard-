from pathlib import Path

import pandas as pd
import pytest

from finance_insights.validation import REQUIRED_COLUMNS, clean_transactions


def valid_frame():
    return pd.DataFrame(
        {
            "date": ["2026-02-01", "2026-01-01"],
            "description": ["  Consulting  ", "Software"],
            "category": [" Income ", "Tools"],
            "amount": ["1200", "-30.50"],
        }
    )


def test_clean_transactions_normalizes_and_sorts():
    result = clean_transactions(valid_frame())
    assert result["date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-01-01", "2026-02-01"]
    assert result["description"].tolist() == ["Software", "Consulting"]
    assert result["category"].tolist() == ["Tools", "Income"]
    assert result["amount"].tolist() == [-30.5, 1200.0]


def test_clean_transactions_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        clean_transactions(valid_frame().drop(columns="category"))


def test_clean_transactions_rejects_empty_frame():
    with pytest.raises(ValueError, match="at least one"):
        clean_transactions(pd.DataFrame(columns=REQUIRED_COLUMNS))


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [("date", "not-a-date", "Invalid date"), ("amount", "many", "Invalid amount")],
)
def test_clean_transactions_rejects_invalid_values(column, value, message):
    frame = valid_frame()
    frame.loc[0, column] = value
    with pytest.raises(ValueError, match=message):
        clean_transactions(frame)


@pytest.mark.parametrize("column", ["description", "category"])
def test_clean_transactions_rejects_missing_text_cells(column):
    frame = valid_frame()
    frame.loc[0, column] = None
    with pytest.raises(ValueError, match=column):
        clean_transactions(frame)


@pytest.mark.parametrize("value", [float("inf"), float("-inf")])
def test_clean_transactions_rejects_non_finite_amounts(value):
    frame = valid_frame()
    frame.loc[0, "amount"] = value
    with pytest.raises(ValueError, match="finite"):
        clean_transactions(frame)


def test_sample_dataset_contract():
    path = Path("data/sample_transactions.csv")
    assert path.exists()
    frame = clean_transactions(pd.read_csv(path))
    assert len(frame) >= 36
    assert frame["date"].dt.to_period("M").nunique() >= 6
    assert (frame["amount"] > 0).any()
    assert (frame["amount"] < 0).any()
    assert frame["category"].nunique() >= 6
