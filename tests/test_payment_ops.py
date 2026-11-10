"""Tests for the optional payment operations feature."""

import pandas as pd
import pytest

from finance_insights.payment_ops import (
    approval_by, failure_reasons, payment_kpis, validate_payments,
)


def sample():
    return pd.DataFrame({
        "transaction_id": ["p1", "p2", "p3", "p4", "p5"],
        "date": ["2026-11-01"] * 5,
        "provider": ["A", "A", "A", "B", "B"],
        "bank": ["X", "X", "Y", "X", "Y"],
        "country": ["RS", "RS", "RS", "FR", "FR"],
        "status": ["approved", "failed", "pending", "approved", "failed"],
        "amount": [100, 25, 80, 60, 30],
        "currency": ["EUR"] * 5,
        "decline_reason": ["", "Insufficient funds", "", "", ""],
    })


def test_kpis_exclude_pending_from_approval_rate_denominator():
    assert payment_kpis(validate_payments(sample())) == {
        "total": 5, "approved": 2, "failed": 2, "pending": 1,
        "resolved": 4, "approval_rate_pct": 50.0,
    }


def test_breakdown_handles_pending_and_missing_outcome_classes():
    result = approval_by(validate_payments(sample()), "provider")
    assert result["provider"].tolist() == ["A", "B"]
    assert result["approved"].tolist() == [1, 1]
    assert result["pending"].tolist() == [1, 0]
    assert result["approval_rate_pct"].tolist() == [50.0, 50.0]


def test_no_resolved_payments_has_no_approval_rate():
    frame = sample().iloc[[2]].copy()
    assert payment_kpis(validate_payments(frame))["approval_rate_pct"] is None
    assert pd.isna(approval_by(validate_payments(frame), "provider")["approval_rate_pct"].iloc[0])


def test_missing_reason_is_explicitly_reported():
    assert failure_reasons(validate_payments(sample())).to_dict("records") == [
        {"reason": "Insufficient funds", "count": 1},
        {"reason": "Unspecified", "count": 1},
    ]


def test_duplicate_ids_rejected():
    frame = sample()
    frame.loc[1, "transaction_id"] = "p1"
    with pytest.raises(ValueError, match="Duplicate"):
        validate_payments(frame)


@pytest.mark.parametrize("status", ["unknown", "", None])
def test_invalid_status_rejected(status):
    frame = sample()
    frame.loc[0, "status"] = status
    with pytest.raises(ValueError, match="status|Status"):
        validate_payments(frame)


def test_nonfinite_or_negative_amount_rejected():
    for amount in [float("inf"), -5, "garbage"]:
        frame = sample()
        frame["amount"] = frame["amount"].astype(object)
        frame.loc[0, "amount"] = amount
        with pytest.raises(ValueError, match="Amounts"):
            validate_payments(frame)


def test_unsupported_breakdown_rejected():
    with pytest.raises(ValueError, match="Unsupported"):
        approval_by(validate_payments(sample()), "transaction_id")
