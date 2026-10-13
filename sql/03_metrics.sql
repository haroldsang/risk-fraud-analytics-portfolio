-- Denominators are transaction-level, not account-level.
WITH Counts AS (
 SELECT COUNT(*) AS transactions,
 SUM(alert) AS alerted_transactions,
 SUM(CASE WHEN alert=1 AND synthetic_fraud_label=1 THEN 1 ELSE 0 END) AS tp,
 SUM(CASE WHEN alert=1 AND synthetic_fraud_label=0 THEN 1 ELSE 0 END) AS fp,
 SUM(CASE WHEN alert=0 AND synthetic_fraud_label=1 THEN 1 ELSE 0 END) AS fn,
 SUM(CASE WHEN alert=0 AND synthetic_fraud_label=0 THEN 1 ELSE 0 END) AS tn,
 SUM(CASE WHEN alert=1 THEN amount_usd ELSE 0 END) AS flagged_amount_usd
 FROM dbo.vw_RiskScored
)
SELECT *, 1.0*alerted_transactions/NULLIF(transactions,0) AS alert_rate,
 1.0*tp/NULLIF(tp+fp,0) AS precision,
 1.0*tp/NULLIF(tp+fn,0) AS recall,
 1.0*fp/NULLIF(fp+tn,0) AS false_positive_rate
FROM Counts;

SELECT CAST(event_time AS date) AS event_date, COUNT(*) AS transactions,
 SUM(alert) AS alerts, 1.0*SUM(alert)/COUNT(*) AS alert_rate
FROM dbo.vw_RiskScored GROUP BY CAST(event_time AS date) ORDER BY event_date;
