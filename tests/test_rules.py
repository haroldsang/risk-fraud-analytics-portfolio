import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from run import detect, generate, metrics


class RulesTest(unittest.TestCase):
    def test_reproducible(self):
        self.assertEqual(generate(), generate())

    def test_velocity_boundary_and_no_future_leak(self):
        template = generate()[0]
        rows = [{**template, 'transaction_id': str(i), 'account_id': 'A',
                 'event_time': f'2026-01-01T00:0{i}:00', 'event_type': 'payment',
                 'device_id': 'D', 'synthetic_fraud_label': 0} for i in range(5)]
        result = detect(list(reversed(rows)))
        self.assertNotIn('R03', result[3]['rule_ids'])
        self.assertIn('R03', result[4]['rule_ids'])
        later = {**rows[0], 'transaction_id': 'later', 'event_time': '2026-01-01T00:15:01'}
        self.assertEqual(detect(rows + [later])[-1]['velocity_10m'], 1)

    def test_device_association_is_as_of_event(self):
        template = generate()[0]
        rows = [{**template, 'transaction_id': str(i), 'account_id': str(i),
                 'device_id': 'shared', 'event_time': f'2026-01-01T00:0{i}:00'} for i in range(3)]
        result = detect(rows)
        self.assertNotIn('R05', result[1]['rule_ids'])
        self.assertIn('R05', result[2]['rule_ids'])

    def test_confusion_matrix(self):
        result = metrics(detect(generate()))
        self.assertEqual(sum(result[k] for k in ('true_positive', 'false_positive', 'false_negative', 'true_negative')), result['transactions'])
        self.assertGreater(result['false_positive'], 0)
        self.assertGreater(result['false_negative'], 0)

    def test_withdrawal_kyc_and_mfa_amount_boundary(self):
        template = {**generate()[0], 'event_type': 'withdrawal', 'kyc_status': 'pending',
                    'mfa_passed': 0, 'amount_usd': 499.99}
        below = detect([template])[0]
        self.assertIn('R01', below['rule_ids'])
        self.assertNotIn('R02', below['rule_ids'])
        at = detect([{**template, 'amount_usd': 500}])[0]
        self.assertIn('R02', at['rule_ids'])

    def test_recent_payment_boundary_and_account_age(self):
        template = generate()[0]
        payment = {**template, 'transaction_id': '1', 'event_type': 'payment',
                   'event_time': '2026-01-01T00:00:00'}
        withdrawal = {**template, 'transaction_id': '2', 'event_type': 'withdrawal',
                      'account_age_days': 7, 'event_time': '2026-01-01T00:30:00'}
        self.assertIn('R04', detect([payment, withdrawal])[1]['rule_ids'])
        self.assertNotIn('R04', detect([payment, {**withdrawal, 'event_time': '2026-01-01T00:30:01'}])[1]['rule_ids'])
        self.assertNotIn('R04', detect([payment, {**withdrawal, 'account_age_days': 8}])[1]['rule_ids'])


if __name__ == '__main__':
    unittest.main()
