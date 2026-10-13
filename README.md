# Risk & Fraud Analytics Portfolio

**Payment-to-withdrawal risk monitoring with SQL Server, Python, and a Power BI reproduction guide.**

This portfolio demonstrates transaction investigation, KYC/MFA signal analysis, withdrawal tracing, account linkage, rule implementation, and honest performance reporting. It is designed for Risk / Fraud Analyst interviews. It uses entirely fabricated data and independently invented rules; no former-employer records, customer information, internal thresholds, or confidential processes are included.

## First project: Payment Risk Monitor

Business question: which transactions warrant analyst review, and how much review workload do the rules create?

- 300 simulated accounts and 3,600 payment/withdrawal events.
- Five interpretable rules with event-time features and no future-data leakage.
- Synthetic labels with both difficult positives and legitimate lookalikes.
- Reproducible CSV exports, transaction-level metrics, and an offline HTML dashboard.
- SQL Server schema, equivalent rule view, and KPI queries.

## Run locally

Requires Python 3.10 or later. The core workflow uses only the standard library; no package installation or credentials are required.

```sh
python src/run.py
python -m unittest discover -s tests -v
```

Open `reports/dashboard.html` in a browser. The generator deterministically replaces the supplied synthetic data and report files. Use `reports/transactions_scored.csv` to inspect an alert timeline. All timestamps represent a synthetic UTC clock.

## SQL Server

Use a dedicated portfolio database. Run `sql/01_schema.sql`, import `data/transactions.csv` into dbo.Transactions, then run `sql/02_rules.sql` and `sql/03_metrics.sql`. The script documents SSMS and optional server-side CSV import. SQL Server 2019+ is the intended target. SQL execution requires your own SQL Server instance and has not been validated against a live server here.

## Power BI and visual example

Follow [the Power BI guide](docs/power_bi.md) to build KPI cards, daily trends, rule-trigger bars, and transaction drilldowns. [Open the offline example](reports/dashboard.html) after downloading the repository; GitHub does not render HTML dashboards directly. A native Power BI workbook is not included.

## Repository map

| Folder | Purpose |
|---|---|
| src | Reproducible generator, detection, metrics, HTML reporting |
| sql | SQL Server schema, features/rules, metric queries |
| data | Entirely synthetic source CSV |
| reports | Scored transactions, summary CSVs, metrics, dashboard |
| docs | Data dictionary, rule assumptions, Power BI instructions |
| tests | Boundary, as-of-event, reproducibility, and metric checks |

See [data dictionary](docs/data_dictionary.md) and [rules and metrics](docs/rules_and_metrics.md) for precise definitions and limitations.

## Reproducible sample results

Seed 42 produces 296 alerts out of 3,600 transactions (8.22%). The confusion matrix contains 293 true positives, 3 false positives, 79 false negatives, and 3,225 true negatives. Precision is 98.99%, recall is 78.76%, and the false positive rate is 0.09%. These high precision results reflect the deliberately simplified generator, not real-world validation.

Six automated Python tests cover reproducibility, trailing-window boundaries, event-time device associations, KYC/MFA conditions, withdrawal tracing, and confusion-matrix accounting. SQL Server and Power BI execution require separate validation in those applications.

## Interpretation and interview discussion

Alerts are review suggestions, not confirmed fraud. Flagged USD is review exposure, not avoided losses. Precision/recall evaluate injected labels only; they do not establish production performance. The synthetic generator deliberately makes many suspicious events obvious. Discuss how to tune thresholds to review capacity, prevent future-data leakage, handle shared-device false positives, and measure outcomes after labels mature.

This repository supports a practical interview walkthrough: explain the payment-to-withdrawal timeline, show Python/SQL rule definitions, inspect an alert, then explain false positives and missed positives. It makes no claim about the author's previous employers or business impact.
