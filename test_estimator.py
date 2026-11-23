import unittest
from estimator import Scenario, evaluate

class TestEstimator(unittest.TestCase):
    def scenario(self, **overrides):
        base = dict(company='Demo',users=5,storage_tb=1,current_storage_monthly=300,
            current_admin_monthly=100,proposed_storage_per_gb_month=0.1,
            proposed_admin_monthly=50,proposed_licenses_monthly=25,
            one_time_migration=500,contingency_pct=20,annual_growth_pct=10)
        base.update(overrides)
        return Scenario(**base)

    def test_known_costs(self):
        r = evaluate(self.scenario())
        self.assertEqual(r['current_monthly'],400)
        self.assertEqual(r['proposed_monthly'],177.4)
        self.assertEqual(r['migration_with_contingency'],600)
        self.assertEqual(r['first_year_difference'],2071.2)
        self.assertEqual(r['payback_months'],2.7)

    def test_no_savings_no_payback(self):
        r = evaluate(self.scenario(proposed_licenses_monthly=500))
        self.assertIsNone(r['payback_months'])
        self.assertLess(r['first_year_difference'],0)

    def test_invalid_storage(self):
        with self.assertRaises(ValueError):
            evaluate(self.scenario(storage_tb=0))

    def test_invalid_cost(self):
        with self.assertRaises(ValueError):
            evaluate(self.scenario(one_time_migration=-1))

if __name__ == '__main__':
    unittest.main()
