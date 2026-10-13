# Rules and measurement

These are independently invented, illustrative thresholds, not former-employer controls or production recommendations.

| Rule | Trigger | Analyst rationale | Common legitimate explanation |
|---|---|---|---|
| R01_KYC_WITHDRAWAL | Withdrawal with pending KYC | Review verification state before release | Verification delay |
| R02_MFA_HIGH_VALUE | Withdrawal >= $500 with failed MFA | Review authentication and amount | User authentication issue |
| R03_VELOCITY_10M | At least five account events in ten minutes | Review bursts of activity | Busy legitimate customer |
| R04_RAPID_WITHDRAWAL | Account age <=7 days, withdrawal after payment within 30 minutes | Trace rapid movement of funds | Legitimate new account |
| R05_SHARED_DEVICE | Device observed on at least three distinct accounts so far | Review account linkage | Shared household device |

The current transaction counts toward velocity and device association. Recent payment must precede the current event. At equal timestamps, transaction ID breaks ties. All windows have inclusive lower bounds. Amount thresholds are inclusive. Country, labels, and scenario never affect detection.

Metrics: precision = TP/(TP+FP); recall = TP/(TP+FN); false positive rate = FP/(FP+TN); alert rate = (TP+FP)/all transactions. Flagged amount is review exposure, **not prevented loss**. Rules overlap, so adding rule counts overstates alert volume. A case-management system would also deduplicate transactions into account cases; this demo does not.

The generator deliberately injects correlated high-velocity positives, quiet positives missed by the rules, and pending-KYC legitimate withdrawals. This is a demonstration of measurement, not evidence of real predictive performance. A real validation would require matured labels, a time-based holdout, delayed-label handling, drift monitoring, calibrated review capacity, and privacy-approved inputs.

Suggested review workflow: inspect account timeline → verify KYC/MFA context → trace payment-to-withdrawal sequence → check device-linked accounts → record evidence and disposition. Alerts do not establish fraud or automatically block transactions.
