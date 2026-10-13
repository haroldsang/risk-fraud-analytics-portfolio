-- SQL Server 2019+. Run in a dedicated portfolio database.
-- All source data is fabricated. Labels/scenarios are evaluation metadata only.
CREATE TABLE dbo.Transactions (
    transaction_id varchar(20) NOT NULL PRIMARY KEY,
    account_id varchar(20) NOT NULL,
    event_time datetime2(0) NOT NULL,
    event_type varchar(20) NOT NULL,
    amount_usd decimal(12,2) NOT NULL,
    kyc_status varchar(20) NOT NULL,
    mfa_passed bit NOT NULL,
    device_id varchar(20) NOT NULL,
    country varchar(2) NOT NULL,
    account_age_days int NOT NULL,
    synthetic_fraud_label bit NOT NULL,
    scenario varchar(100) NOT NULL
);
CREATE INDEX IX_Transactions_AccountTime ON dbo.Transactions(account_id, event_time);
CREATE INDEX IX_Transactions_DeviceTime ON dbo.Transactions(device_id, event_time);
-- Import data/transactions.csv using SSMS Import Flat File / Import Wizard.
-- Map the CSV columns to this existing table in the order above.
-- event_time uses ISO 8601; mfa_passed/label are numeric 0/1.
-- Optional server-side import (replace with a path accessible to the SQL service):
-- BULK INSERT dbo.Transactions FROM 'C:\portfolio\data\transactions.csv'
-- WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', ROWTERMINATOR='0x0a');
