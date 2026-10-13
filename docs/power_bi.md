# Power BI reproduction guide

The checked-in HTML dashboard is a runnable visual example. A native `.pbix` file is not included.

1. Run `python src/run.py`.
2. In Power BI Desktop, import `reports/transactions_scored.csv` and `reports/rule_summary.csv` using Get Data → Text/CSV.
3. Name the transaction table `Transactions`. Set event_time to Date/Time; amount_usd to decimal; alert, rule_count, mfa_passed, and synthetic_fraud_label to whole numbers. Keep account/device/transaction IDs as text.
4. Add these measures; display ratios as percentages and exposure as USD.

```dax
Transactions Count = COUNTROWS(Transactions)
Alerted Transactions = CALCULATE([Transactions Count], Transactions[alert] = 1)
Alert Rate = DIVIDE([Alerted Transactions], [Transactions Count])
TP = CALCULATE([Transactions Count], Transactions[alert] = 1, Transactions[synthetic_fraud_label] = 1)
FP = CALCULATE([Transactions Count], Transactions[alert] = 1, Transactions[synthetic_fraud_label] = 0)
FN = CALCULATE([Transactions Count], Transactions[alert] = 0, Transactions[synthetic_fraud_label] = 1)
TN = CALCULATE([Transactions Count], Transactions[alert] = 0, Transactions[synthetic_fraud_label] = 0)
Precision = DIVIDE([TP], [TP] + [FP])
Recall = DIVIDE([TP], [TP] + [FN])
False Positive Rate = DIVIDE([FP], [FP] + [TN])
Flagged Amount USD = CALCULATE(SUM(Transactions[amount_usd]), Transactions[alert] = 1)
```

5. Create cards for volume, alerts, precision, recall, and false positive rate. Add a daily alert-rate line chart, a bar chart from rule_summary, and a transaction drilldown table containing event_time, account_id, event_type, amount_usd, kyc_status, mfa_passed, velocity_10m, and rule_ids.
6. Add slicers for event date, event_type, and kyc_status. The rule-summary chart is a static overall export; it does not respond to transaction slicers. For interactive rule analysis, split rule_ids into rows in a separate bridge table in Power Query and relate it using transaction_id.
7. Label every page “Synthetic data / illustrative rules”. Do not describe flagged amounts as savings or fraud losses. Verify unfiltered cards against metrics.json before taking screenshots.

SQL Server alternative: import dbo.vw_RiskScored using Import mode. Rename columns/adjust measures as needed; SQL stores rule flags separately. DAX instructions are supplied for reproduction and have not been executed in Power BI Desktop in this environment.
