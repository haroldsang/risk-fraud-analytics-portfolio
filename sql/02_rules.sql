-- Event ordering matches Python: event_time, then transaction_id.
-- Inclusive 10-minute / 30-minute boundaries. No future observations.
CREATE OR ALTER VIEW dbo.vw_RiskScored AS
WITH Features AS (
    SELECT t.*,
       (SELECT COUNT(*) FROM dbo.Transactions p
        WHERE p.account_id=t.account_id
          AND p.event_time >= DATEADD(minute,-10,t.event_time)
          AND (p.event_time<t.event_time OR
               (p.event_time=t.event_time AND p.transaction_id<=t.transaction_id))) AS velocity_10m,
       (SELECT COUNT(DISTINCT p.account_id) FROM dbo.Transactions p
        WHERE p.device_id=t.device_id
          AND (p.event_time<t.event_time OR
               (p.event_time=t.event_time AND p.transaction_id<=t.transaction_id))) AS device_accounts,
       CASE WHEN EXISTS (SELECT 1 FROM dbo.Transactions p
        WHERE p.account_id=t.account_id AND p.event_type='payment'
          AND p.event_time >= DATEADD(minute,-30,t.event_time)
          AND (p.event_time<t.event_time OR
               (p.event_time=t.event_time AND p.transaction_id<t.transaction_id)))
        THEN 1 ELSE 0 END AS recent_payment
    FROM dbo.Transactions t
), Flags AS (
    SELECT *,
       CASE WHEN event_type='withdrawal' AND kyc_status<>'verified' THEN 1 ELSE 0 END AS r01,
       CASE WHEN event_type='withdrawal' AND mfa_passed=0 AND amount_usd>=500 THEN 1 ELSE 0 END AS r02,
       CASE WHEN velocity_10m>=5 THEN 1 ELSE 0 END AS r03,
       CASE WHEN event_type='withdrawal' AND recent_payment=1 AND account_age_days<=7 THEN 1 ELSE 0 END AS r04,
       CASE WHEN device_accounts>=3 THEN 1 ELSE 0 END AS r05
    FROM Features
)
SELECT *, r01+r02+r03+r04+r05 AS rule_count,
    CASE WHEN r01+r02+r03+r04+r05>0 THEN 1 ELSE 0 END AS alert
FROM Flags;
GO
