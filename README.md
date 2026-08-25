# Finance Insights Dashboard

A small business analytics app that turns a transaction CSV into readable KPIs, expense breakdowns, monthly trends, unusually large transaction flags, and a cleaned downloadable report.

## Live demo

The app is ready for Streamlit Community Cloud. A public URL and application screenshot will be added after the GitHub repository is published.

## Why this project

Transaction exports are easy to obtain but often difficult to review quickly. This project demonstrates a complete data workflow: schema validation, cleaning, aggregation, explainable anomaly detection, visualization, plain-language insights, testing, and export.

## Features

- Upload a CSV or explore six months of bundled synthetic data.
- Validate dates, amounts, required columns, and empty values.
- Calculate income, expenses, balance, and savings rate.
- Compare monthly income, expenses, and balance.
- Analyze spending by category and inspect the largest transactions.
- Flag unusually large amounts with a transparent IQR rule.
- Generate deterministic business observations without a paid AI API.
- Download the cleaned dataset as CSV.

## CSV schema

| Column | Type | Example | Meaning |
| --- | --- | --- | --- |
| `date` | `YYYY-MM-DD` | `2026-06-03` | Transaction date |
| `description` | text | `Client retainer` | Human-readable label |
| `category` | text | `Income` | Reporting category |
| `amount` | number | `4800` or `-950` | Positive is income; negative is expense |

See [`data/sample_transactions.csv`](data/sample_transactions.csv) for a complete example. The sample is synthetic and contains no personal or confidential information.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
streamlit run app.py
```

Then open the local address printed by Streamlit.

## Tests and code quality

```bash
pytest -v
ruff check src tests app.py
```

The tests cover cleaning, validation failures, KPI calculations, category aggregation, monthly summaries, ranking, anomaly detection, insight generation, and the Streamlit entrypoint.

## Architecture

```text
CSV or sample data
        ↓
validation.py — schema checks, type conversion, cleanup
        ↓
analytics.py — KPIs, categories, months, ranking, IQR anomalies
        ↓
insights.py — deterministic plain-language observations
        ↓
app.py — Streamlit controls, Plotly charts, tables, CSV export
```

## Anomaly rule

The app calculates the absolute value of each transaction amount, then flags values above:

`Q3 + 1.5 × (Q3 - Q1)`

This standard interquartile-range rule is explainable and resistant to a small number of extreme values. A flag means “review this transaction,” not “this transaction is incorrect.”

## Design decisions

- Pure pandas functions keep business logic independent from Streamlit and easy to test.
- Positive/negative amount conventions make the input format simple.
- Automated insights are deterministic so every statement can be traced to a calculation.
- The app uses no bank connection, database, authentication, paid API, or uploaded-data storage.

## Limitations

- Currency is displayed as US dollars for demonstration and is not converted.
- Categories are accepted as provided; equivalent labels are not automatically merged.
- The IQR rule may be less informative for very small or unusually uniform datasets.
- There is no forecasting, budgeting recommendation, or financial advice.
- Uploaded data is processed only in the running app session.

## AI-assisted development

AI coding assistance helped structure the modules, draft test cases, and review edge cases. Outputs were verified with explicit expected-value tests, a clean-environment install, Ruff, and a Streamlit smoke test. Synthetic figures were reviewed for schema coverage rather than treated as real business data.

## CV-ready bullets

- Built a tested Streamlit finance dashboard with pandas and Plotly that validates transaction CSVs, calculates KPIs, visualizes monthly/category trends, and exports cleaned reports.
- Implemented explainable IQR anomaly detection and deterministic business insights, with automated tests covering invalid inputs and core analytical calculations.

## License

MIT License. See [`LICENSE`](LICENSE).
