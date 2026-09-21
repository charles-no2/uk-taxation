import unittest
from datetime import date

from fetch_exchange_rates import extract_rates, periods


class RateTests(unittest.TestCase):
    def payload(self, rate='10'):
        return {'data': {'attributes': {'year': '2025', 'month': '4', 'type': 'monthly'}},
                'included': [{'type': 'exchange_rate', 'attributes': {
                    'currency_code': 'HKD', 'country': 'Hong Kong', 'rate': rate,
                    'validity_start_date': '2025-04-01', 'validity_end_date': '2025-04-30'}}]}

    def test_rate_direction(self):
        rows = extract_rates(self.payload(), date(2025, 4, 1), {'HKD'}, 'url', 'stamp')
        self.assertEqual(rows[0]['currency_units_per_gbp'], '10')
        self.assertEqual(rows[0]['gbp_per_currency_unit'], '0.100000000000')

    def test_missing_currency_and_invalid_rates_fail(self):
        for rate in ['0', '-1', 'NaN', 'Infinity']:
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                extract_rates(self.payload(rate), date(2025, 4, 1), {'HKD'}, '', '')
        with self.assertRaises(ValueError):
            extract_rates(self.payload(), date(2025, 4, 1), {'USD'}, '', '')

    def test_wrong_period_and_incomplete_coverage_fail(self):
        with self.assertRaises(ValueError):
            extract_rates(self.payload(), date(2025, 5, 1), {'HKD'}, '', '')
        payload = self.payload()
        payload['included'][0]['attributes']['validity_end_date'] = '2025-04-29'
        with self.assertRaises(ValueError):
            extract_rates(payload, date(2025, 4, 1), {'HKD'}, '', '')

    def test_months_cross_year(self):
        self.assertEqual(list(periods(date(2025, 12, 28), date(2026, 2, 1))),
                         [date(2025, 12, 1), date(2026, 1, 1), date(2026, 2, 1)])


if __name__ == '__main__':
    unittest.main()
