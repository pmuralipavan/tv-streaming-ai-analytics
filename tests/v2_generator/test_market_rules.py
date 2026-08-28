import copy
import unittest
from pathlib import Path

from src.v2_generator.market_rules import (
    load_market_rules,
    validate_market_rules,
)


class TestMarketRules(unittest.TestCase):

    def setUp(self):
        self.rules = load_market_rules(
            Path("config/v2_market_rules.json")
        )

    def test_valid_market_rules_load(self):
        self.assertEqual(
            set(self.rules["platform_rules"]),
            {"Linear TV", "Streaming"},
        )

        self.assertEqual(
            len(self.rules["monthly_demand_multipliers"]),
            12,
        )

        self.assertEqual(
            len(self.rules["monthly_inventory_multipliers"]),
            12,
        )

    def test_platform_weights_must_total_one(self):
        invalid_rules = copy.deepcopy(self.rules)

        invalid_rules["advertiser_platform_weights"][
            "Balanced"
        ]["Streaming"] = 0.6

        with self.assertRaisesRegex(
            ValueError,
            "platform weights must total 1.0",
        ):
            validate_market_rules(invalid_rules)

    def test_all_twelve_months_are_required(self):
        invalid_rules = copy.deepcopy(self.rules)

        del invalid_rules[
            "monthly_demand_multipliers"
        ]["12"]

        with self.assertRaisesRegex(
            ValueError,
            "must contain months 1 through 12",
        ):
            validate_market_rules(invalid_rules)

    def test_excessive_growth_rate_is_rejected(self):
        invalid_rules = copy.deepcopy(self.rules)

        invalid_rules["platform_rules"]["Streaming"][
            "annual_demand_growth_rate"
        ] = 0.5

        with self.assertRaisesRegex(
            ValueError,
            "must be between -0.20 and 0.20",
        ):
            validate_market_rules(invalid_rules)


if __name__ == "__main__":
    unittest.main()