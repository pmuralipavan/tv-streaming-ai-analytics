import unittest
from pathlib import Path

from src.v2_generator.config import load_config
from src.v2_generator.inventory_data import generate_inventory
from src.v2_generator.market_rules import load_market_rules
from src.v2_generator.reference_data import (
    build_content_reference_frames,
    build_media_reference_frames,
    load_content_catalog,
    load_media_catalog,
)


class TestInventoryData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = load_config(
            Path("config/v2_generator_config.json")
        )

        cls.market_rules = load_market_rules(
            Path("config/v2_market_rules.json")
        )

        media_catalog = load_media_catalog(
            Path("config/v2_media_catalog.json")
        )

        cls.companies_df, cls.properties_df = (
            build_media_reference_frames(media_catalog)
        )

        content_catalog = load_content_catalog(
            Path("config/v2_content_catalog.json")
        )

        cls.programs_df, cls.bridge_df = (
            build_content_reference_frames(
                content_catalog,
                cls.companies_df,
                cls.properties_df,
            )
        )

        cls.inventory_df = generate_inventory(
            start_date=cls.config.start_date,
            end_date=cls.config.end_date,
            random_seed=cls.config.random_seed,
            market_rules=cls.market_rules,
            properties_df=cls.properties_df,
            programs_df=cls.programs_df,
            program_property_bridge_df=cls.bridge_df,
        )

    def test_expected_inventory_row_count(self):
        self.assertEqual(len(self.inventory_df), 5724)

    def test_inventory_grain_is_unique(self):
        duplicate_count = self.inventory_df.duplicated(
            subset=[
                "inventory_month",
                "property_id",
                "program_id",
                "daypart",
            ]
        ).sum()

        self.assertEqual(duplicate_count, 0)

    def test_linear_drama_uses_scheduled_dayparts(self):
        linear_drama_dayparts = set(
            self.inventory_df[
                (
                    self.inventory_df["property_id"]
                    == "MP001"
                )
                & (
                    self.inventory_df["program_id"]
                    == "PG001"
                )
            ]["daypart"]
        )

        self.assertEqual(
            linear_drama_dayparts,
            {"Primetime", "Late Night"},
        )

    def test_streaming_drama_has_broader_availability(self):
        streaming_drama_dayparts = set(
            self.inventory_df[
                (
                    self.inventory_df["property_id"]
                    == "MP002"
                )
                & (
                    self.inventory_df["program_id"]
                    == "PG001"
                )
            ]["daypart"]
        )

        self.assertEqual(
            streaming_drama_dayparts,
            {
                "Morning",
                "Daytime",
                "Early Fringe",
                "Primetime",
                "Late Night",
            },
        )

    def test_inventory_is_reproducible(self):
        repeated_inventory_df = generate_inventory(
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            random_seed=self.config.random_seed,
            market_rules=self.market_rules,
            properties_df=self.properties_df,
            programs_df=self.programs_df,
            program_property_bridge_df=self.bridge_df,
        )

        self.assertTrue(
            self.inventory_df.equals(repeated_inventory_df)
        )


if __name__ == "__main__":
    unittest.main()