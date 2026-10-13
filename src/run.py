"""Deterministic synthetic payment-risk portfolio. Python 3.10+, no dependencies."""
import csv
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
FIELDS = ['transaction_id', 'account_id', 'event_time', 'event_type', 'amount_usd',
          'kyc_status', 'mfa_passed', 'device_id', 'country', 'account_age_days',
          'synthetic_fraud_label', 'scenario']


def generate():
    rng = random.Random(SEED)
    rows = []
    base = datetime(2026, 1, 1)
    for a in range(1, 301):
        account = f'ACC-{a:04d}'
        suspicious = a % 10 == 0
        for j in range(12):
            at = base + timedelta(days=a % 28, hours=j if not suspicious else 0,
                                  minutes=rng.randrange(0, 5) if suspicious else rng.randrange(60))
            kind = 'withdrawal' if j in (8, 10, 11) else 'payment'
            rows.append(dict(transaction_id=f'TXN-{len(rows)+1:06d}', account_id=account,
                event_time=at.isoformat(timespec='seconds'), event_type=kind,
                amount_usd=round(rng.uniform(800, 1600) if suspicious else rng.uniform(5, 450), 2),
                kyc_status='pending' if suspicious and a % 20 == 0 else 'verified',
                mfa_passed=0 if suspicious or rng.random() < .025 else 1,
                device_id=f'DEV-{a//30:03d}' if suspicious else f'DEV-{a:04d}',
                country='US', account_age_days=2 if suspicious else rng.randrange(10, 500),
                synthetic_fraud_label=int(suspicious),
                scenario='injected_high_velocity' if suspicious else 'baseline'))
    # Difficult positive examples and legitimate lookalikes prevent a perfect toy score.
    for row in rows[120:132]:
        row['synthetic_fraud_label'] = 1
        row['scenario'] = 'quiet_fraud_not_detectable_by_demo_rules'
    for row in rows[240:252]:
        row['kyc_status'] = 'pending'
        row['scenario'] = 'legitimate_pending_kyc'
    return sorted(rows, key=lambda r: (r['event_time'], r['transaction_id']))


def detect(rows):
    history = defaultdict(list)
    device_accounts = defaultdict(set)
    results = []
    for row in sorted(rows, key=lambda r: (r['event_time'], r['transaction_id'])):
        at = datetime.fromisoformat(row['event_time'])
        prior = history[row['account_id']]
        # Past/current observations only: no future device associations or transactions.
        device_accounts[row['device_id']].add(row['account_id'])
        velocity = sum(t >= at - timedelta(minutes=10) for t, _ in prior) + 1
        recent_payment = any(t >= at - timedelta(minutes=30) and kind == 'payment'
                             for t, kind in prior)
        reasons = []
        if row['event_type'] == 'withdrawal' and row['kyc_status'] != 'verified':
            reasons.append('R01_KYC_WITHDRAWAL')
        if row['event_type'] == 'withdrawal' and not int(row['mfa_passed']) and float(row['amount_usd']) >= 500:
            reasons.append('R02_MFA_HIGH_VALUE')
        if velocity >= 5:
            reasons.append('R03_VELOCITY_10M')
        if row['event_type'] == 'withdrawal' and recent_payment and int(row['account_age_days']) <= 7:
            reasons.append('R04_RAPID_WITHDRAWAL')
        if len(device_accounts[row['device_id']]) >= 3:
            reasons.append('R05_SHARED_DEVICE')
        results.append({**row, 'velocity_10m': velocity, 'rule_ids': '|'.join(reasons),
                        'rule_count': len(reasons), 'alert': int(bool(reasons))})
        prior.append((at, row['event_type']))
    return results


def metrics(rows):
    tp = sum(r['alert'] == 1 and int(r['synthetic_fraud_label']) == 1 for r in rows)
    fp = sum(r['alert'] == 1 and int(r['synthetic_fraud_label']) == 0 for r in rows)
    fn = sum(r['alert'] == 0 and int(r['synthetic_fraud_label']) == 1 for r in rows)
    tn = len(rows) - tp - fp - fn
    ratio = lambda a, b: round(a / b, 4) if b else None
    return dict(transactions=len(rows), accounts=len({r['account_id'] for r in rows}),
        total_amount_usd=round(sum(float(r['amount_usd']) for r in rows), 2),
        alerted_transactions=tp + fp, alert_rate=ratio(tp + fp, len(rows)),
        precision=ratio(tp, tp + fp), recall=ratio(tp, tp + fn), false_positive_rate=ratio(fp, fp + tn),
        true_positive=tp, false_positive=fp, false_negative=fn, true_negative=tn,
        flagged_amount_usd=round(sum(float(r['amount_usd']) for r in rows if r['alert']), 2))


def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    for folder in ('data', 'reports'):
        (ROOT / folder).mkdir(exist_ok=True)
    rows = generate()
    result = detect(rows)
    kpi = metrics(result)
    write_csv(ROOT / 'data/transactions.csv', rows, FIELDS)
    write_csv(ROOT / 'reports/transactions_scored.csv', result,
              FIELDS + ['velocity_10m', 'rule_ids', 'rule_count', 'alert'])
    rule_counts = Counter(rule for r in result for rule in r['rule_ids'].split('|') if rule)
    write_csv(ROOT / 'reports/rule_summary.csv',
              [dict(rule_id=k, triggered_transactions=v) for k, v in sorted(rule_counts.items())],
              ['rule_id', 'triggered_transactions'])
    (ROOT / 'reports/metrics.json').write_text(json.dumps(kpi, indent=2), encoding='utf-8')
    daily = defaultdict(lambda: [0, 0])
    for r in result:
        daily[r['event_time'][:10]][0] += 1
        daily[r['event_time'][:10]][1] += r['alert']
    write_csv(ROOT / 'reports/daily_summary.csv',
        [dict(date=d, transactions=v[0], alerts=v[1], alert_rate=round(v[1]/v[0], 4))
         for d, v in sorted(daily.items())], ['date', 'transactions', 'alerts', 'alert_rate'])
    bars = ''.join(f'<div class="barrow"><span>{key}</span><div class="bar" style="width:{value/max(rule_counts.values())*60:.1f}%"></div><b>{value}</b></div>'
                   for key, value in sorted(rule_counts.items()))
    cards = ''.join(f'<article><small>{name}</small><strong>{value}</strong></article>'
                    for name, value in [('Transactions', kpi['transactions']), ('Alerts', kpi['alerted_transactions']),
                    ('Precision', f"{kpi['precision']:.1%}"), ('Recall', f"{kpi['recall']:.1%}"),
                    ('False positive rate', f"{kpi['false_positive_rate']:.1%}")])
    html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Payment Risk Monitor</title><style>body{font:16px system-ui;background:#101827;color:#e2e8f0;margin:0;padding:40px;max-width:1100px}h1{font-size:32px}p,small{color:#a9bed5}.cards{display:flex;flex-wrap:wrap;gap:16px}article{background:#1e293b;padding:20px;min-width:140px;border-radius:10px}strong{display:block;font-size:28px;margin-top:12px}.barrow{display:flex;align-items:center;gap:12px;margin:18px 0}.barrow span{width:230px}.bar{background:#38bdf8;height:22px;border-radius:4px}footer{margin-top:36px;color:#a9bed5}</style><h1>Payment Risk Monitor</h1><p>Fully synthetic data • January 2026 • Illustrative analyst portfolio</p><section class="cards">''' + cards + '</section><h2>Rule triggers</h2><p>A transaction may trigger multiple rules; counts are not additive.</p>' + bars + '<footer>Flagged amount is exposure for review, not proven fraud loss or prevented loss. Metrics evaluate injected labels only. No production validation.</footer></html>'
    (ROOT / 'reports/dashboard.html').write_text(html, encoding='utf-8')
    print(json.dumps(kpi, indent=2))


if __name__ == '__main__':
    main()
