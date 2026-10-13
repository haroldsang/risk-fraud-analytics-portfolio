# Data dictionary

All records, IDs, amounts, labels, and patterns are generated from scratch with seed 42. Time is a synthetic UTC clock. USD is the sole currency; there is no currency conversion.

| Field | Type | Meaning |
|---|---|---|
| transaction_id | text | Unique synthetic transaction identifier |
| account_id | text | Synthetic customer account; no identity information |
| event_time | ISO datetime | Synthetic UTC event timestamp, seconds precision |
| event_type | text | `payment` or `withdrawal`; simplified successful event |
| amount_usd | decimal | Positive transaction amount, USD |
| kyc_status | text | `verified` or `pending` at event time |
| mfa_passed | 0/1 | Simplified event-level MFA result; no authentication logs |
| device_id | text | Fabricated device association; no actual fingerprint |
| country | text | `US` for all events; no geographical rule in this version |
| account_age_days | integer | Synthetic age at event time |
| synthetic_fraud_label | 0/1 | Injected ground truth for evaluation only; never a detection input |
| scenario | text | Generator annotation for evaluation only; never a detection input |
| velocity_10m | integer | Account transaction count in inclusive trailing ten minutes, including current event |
| rule_ids | text | Pipe-separated triggered Python rule identifiers |
| rule_count | integer | Number of rules triggered |
| alert | 0/1 | At least one rule triggered; analyst review suggestion |

`transactions.csv` contains the first 12 fields. `transactions_scored.csv` adds the four derived fields. SQL exposes the same features with binary `r01` through `r05` rather than a concatenated string. Same-second events are ordered by transaction ID.

`rule_summary.csv`: rule_id, triggered_transactions (overlapping counts).
`daily_summary.csv`: date, transactions, alerts, alert_rate (0–1).
`metrics.json`: overall transaction-level counts, USD totals, and 0–1 ratios. Zero denominators produce null.
