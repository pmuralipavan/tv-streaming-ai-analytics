import unittest
from pathlib import Path

from src.v2_generator.advertiser_data import (
    build_advertiser_frame,
    load_advertiser_catalog,
)


class TestAdvertiserData(unittest.TestCase):

    def test_catalog_builds_expected_counts(self):
        catalog = load_advertiser_catalog(
            Path("config/v2_advertiser_catalog.json")
        )

        advertisers_df = build_advertiser_frame(catalog)

        self.assertEqual(len(advertisers_df), 16)
        self.assertEqual(
            advertisers_df["industry"].nunique(),
            8,
        )

    def test_advertiser_ids_are_unique(self):
        catalog = load_advertiser_catalog(
            Path("config/v2_advertiser_catalog.json")
        )

        advertisers_df = build_advertiser_frame(catalog)

        self.assertFalse(
            advertisers_df["advertiser_id"].duplicated().any()
        )

    def test_invalid_platform_strategy_is_rejected(self):
        catalog = {
            "advertisers": [
                {
                    "advertiser_id": "AD001",
                    "advertiser_name": "Test Advertiser",
                    "industry": "Technology",
                    "size_tier": "Growth",
                    "platform_strategy": "Unknown Strategy",
                    "budget_weight": 1.0,
                }
            ]
        }

        with self.assertRaisesRegex(
            ValueError,
            "Invalid platform strategies",
        ):
            build_advertiser_frame(catalog)

    def test_nonpositive_budget_weight_is_rejected(self):
        catalog = {
            "advertisers": [
                {
                    "advertiser_id": "AD001",
                    "advertiser_name": "Test Advertiser",
                    "industry": "Technology",
                    "size_tier": "Growth",
                    "platform_strategy": "Streaming First",
                    "budget_weight": 0,
                }
            ]
        }

        with self.assertRaisesRegex(
            ValueError,
            "budget_weight must be greater than zero",
        ):
            build_advertiser_frame(catalog)


if __name__ == "__main__":
    unittest.main()