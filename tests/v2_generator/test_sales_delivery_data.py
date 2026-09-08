import unittest

import pandas as pd

from src.v2_generator.sales_delivery_data import (
    generate_sales_delivery,
    validate_sales_delivery_frame,
)

def build_market_rules():
    return {
        "sales_delivery_generation": {
            "base_sell_through_rate_by_platform": {
                "Linear TV": 0.78,
                "Streaming": 0.82,
            },
            "minimum_sell_through_rate": 0.25,
            "maximum_sell_through_rate": 0.98,
            "impressions_per_inventory_unit": 1000,
            "minimum_delivery_rate": 0.70,
            "maximum_delivery_rate": 1.10,
        },
        "platform_rules": {
           "Linear TV": {
            "delivery_rate_mean": 0.97,
            "delivery_rate_standard_deviation": 0.08,
                    },
           "Streaming": {
            "delivery_rate_mean": 0.96,
            "delivery_rate_standard_deviation": 0.10,
                  },
          },
    }

class TestSalesDeliveryData(unittest.TestCase):
    def test_empty_sales_delivery_frame_is_rejected(self):
        sales_delivery_df = pd.DataFrame(
            columns=[
                "sales_delivery_id",
                "inventory_id",
                "sold_inventory_units",
                "booked_impressions",
                "delivered_impressions",
            ]
        )

        with self.assertRaises(ValueError):
            validate_sales_delivery_frame(
                sales_delivery_df
            )

    def test_duplicate_sales_delivery_ids_are_rejected(self):
        sales_delivery_df = pd.DataFrame(
            [
                {
                    "sales_delivery_id": "SD0000001",
                    "inventory_id": "INV0000001",
                    "sold_inventory_units": 10,
                    "booked_impressions": 1000,
                    "delivered_impressions": 950,
                },
                {
                    "sales_delivery_id": "SD0000001",
                    "inventory_id": "INV0000002",
                    "sold_inventory_units": 12,
                    "booked_impressions": 1200,
                    "delivered_impressions": 1100,
                },
            ]
        )

        with self.assertRaises(ValueError):
            validate_sales_delivery_frame(
                sales_delivery_df
            )
    def test_negative_sold_inventory_units_are_rejected(self):
        sales_delivery_df = pd.DataFrame(
            [
                {
                    "sales_delivery_id": "SD0000001",
                    "inventory_id": "INV0000001",
                    "sold_inventory_units": -1,
                    "booked_impressions": 1000,
                    "delivered_impressions": 950,
                }
            ]
        )

        with self.assertRaises(ValueError):
            validate_sales_delivery_frame(
                sales_delivery_df
            )
            
    def test_generate_sales_delivery_adds_platform_and_genre(self):
        inventory_df = pd.DataFrame(
            [
                {
                    "inventory_id": "INV0000001",
                    "inventory_month": pd.Timestamp("2026-01-01"),
                    "property_id": "PROP001",
                    "program_id": "PROG001",
                    "daypart": "Primetime",
                    "available_inventory_units": 1000,
                }
            ]
        )

        properties_df = pd.DataFrame(
            [
                {
                    "property_id": "PROP001",
                    "platform": "Streaming",
                }
            ]
        )

        programs_df = pd.DataFrame(
            [
                {
                    "program_id": "PROG001",
                    "genre": "Drama",
                }
            ]
        )

        market_rules = build_market_rules()

        result_df = generate_sales_delivery(
            inventory_df=inventory_df,
            random_seed=42,
            market_rules=market_rules,
            properties_df=properties_df,
            programs_df=programs_df,
        )

        self.assertEqual(
            result_df.loc[0, "platform"],
            "Streaming",
        )

        self.assertEqual(
            result_df.loc[0, "genre"],
            "Drama",
        )

    def test_sold_inventory_units_do_not_exceed_available_inventory(self):
        inventory_df = pd.DataFrame(
            [
                {
                    "inventory_id": "INV0000001",
                    "inventory_month": pd.Timestamp("2026-01-01"),
                    "property_id": "PROP001",
                    "program_id": "PROG001",
                    "daypart": "Primetime",
                    "available_inventory_units": 100,
                }
            ]
        )

        properties_df = pd.DataFrame(
            [
                {
                    "property_id": "PROP001",
                    "platform": "Streaming",
                }
            ]
        )

        programs_df = pd.DataFrame(
            [
                {
                    "program_id": "PROG001",
                    "genre": "Drama",
                }
            ]
        )

        market_rules = build_market_rules()

        result_df = generate_sales_delivery(
            inventory_df=inventory_df,
            random_seed=42,
            market_rules=market_rules,
            properties_df=properties_df,
            programs_df=programs_df,
        )

        self.assertLessEqual(
            result_df.loc[0, "sold_inventory_units"],
            result_df.loc[0, "available_inventory_units"],
        )

    def test_booked_impressions_are_based_on_sold_units(self):
        inventory_df = pd.DataFrame(
            [
                {
                    "inventory_id": "INV0000001",
                    "inventory_month": pd.Timestamp("2026-01-01"),
                    "property_id": "PROP001",
                    "program_id": "PROG001",
                    "daypart": "Primetime",
                    "available_inventory_units": 100,
                }
            ]
        )

        properties_df = pd.DataFrame(
            [
                {
                    "property_id": "PROP001",
                    "platform": "Streaming",
                }
            ]
        )

        programs_df = pd.DataFrame(
            [
                {
                    "program_id": "PROG001",
                    "genre": "Drama",
                }
            ]
        )

        market_rules = build_market_rules()

        result_df = generate_sales_delivery(
            inventory_df=inventory_df,
            random_seed=42,
            market_rules=market_rules,
            properties_df=properties_df,
            programs_df=programs_df,
        )

        self.assertEqual(
            result_df.loc[0, "booked_impressions"],
            result_df.loc[0, "sold_inventory_units"] * 1000,
        )

    def test_delivered_impressions_follow_delivery_rate(self):
        inventory_df = pd.DataFrame(
            [
                {
                    "inventory_id": "INV0000001",
                    "inventory_month": pd.Timestamp("2026-01-01"),
                    "property_id": "PROP001",
                    "program_id": "PROG001",
                    "daypart": "Primetime",
                    "available_inventory_units": 100,
                }
            ]
        )

        properties_df = pd.DataFrame(
            [
                {
                    "property_id": "PROP001",
                    "platform": "Streaming",
                }
            ]
        )

        programs_df = pd.DataFrame(
            [
                {
                    "program_id": "PROG001",
                    "genre": "Drama",
                }
            ]
        )

        result_df = generate_sales_delivery(
            inventory_df=inventory_df,
            random_seed=42,
            market_rules=build_market_rules(),
            properties_df=properties_df,
            programs_df=programs_df,
        ) 

        booked_impressions = int(
            result_df["booked_impressions"].iloc[0]
        )

        delivery_rate = float(
            result_df["delivery_rate"].iloc[0]
        )

        delivered_impressions = int(
            result_df["delivered_impressions"].iloc[0]
        )

        expected_delivered_impressions = round(
            booked_impressions * delivery_rate
        )

        self.assertEqual(
            delivered_impressions,
            expected_delivered_impressions,
        )

        self.assertGreaterEqual(
            delivery_rate,
            0.70,
        )

        self.assertLessEqual(
            delivery_rate,
            1.10,
        )
        


if __name__ == "__main__":
    unittest.main()
