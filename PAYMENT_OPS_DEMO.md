# Payment Operations Analytics — Phase 1 (demo module)

This optional module adds a **synthetic-data-first** foundation for payment-operations analysis. It does not change the existing Finance Insights dashboard.

## Run the demo calculations

```bash
pip install -e ".[dev]"
python -c "import pandas as pd; from finance_insights.payment_ops import validate_payments,payment_kpis,approval_by,failure_reasons; x=validate_payments(pd.read_csv('data/sample_payments.csv')); print(payment_kpis(x)); print(approval_by(x,'provider')); print(failure_reasons(x))"
pytest -q tests/test_payment_ops.py
```

## CSV columns

`transaction_id`, `date` (YYYY-MM-DD), `provider`, `bank`, `country`, `status` (`approved`, `failed`, `pending`), `amount`, `currency`, `decline_reason`.

`transaction_id` should refer to one payment attempt. Do not upload real payment/customer data to a public demo.

## Metric definitions

- **Approval rate:** approved / (approved + failed). Pending transactions are excluded from the denominator.
- **Breakdowns:** transaction outcome counts and approval rate by provider, bank, or country.
- **Failure reasons:** count of declined payments by reason; missing reasons labeled `Unspecified`.
- The module never changes a payment status, blocks an account, or selects a payment route.

## Limitations / next steps

- This is an **analytics engine**, not a client-ready product. A Streamlit view, file-size limits, privacy/security design, validation against a client's own taxonomy, and reviewed deployment configuration are still required.
- The sample is artificial and **does not establish production effectiveness**.
- We do not calculate revenue/volume across currencies or interpret approval rates for tiny samples.
- Clients may use different status names or timestamp formats; add a configurable mapping before importing their exports.
