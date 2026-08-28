import unittest
from pathlib import Path

from src.v2_generator.reference_data import (
    build_content_reference_frames,
    build_media_reference_frames,
    load_content_catalog,
    load_media_catalog,
)


class TestReferenceData(unittest.TestCase):

    def setUp(self):
        media_catalog = load_media_catalog(
            Path("config/v2_media_catalog.json")
        )

        self.companies_df, self.properties_df = (
            build_media_reference_frames(media_catalog)
        )

    def test_media_catalog_builds_expected_counts(self):
        self.assertEqual(len(self.companies_df), 4)
        self.assertEqual(len(self.properties_df), 12)

        self.assertEqual(
            set(self.properties_df["platform"]),
            {"Linear TV", "Streaming"},
        )

    def test_property_company_ids_are_valid(self):
        company_ids = set(self.companies_df["company_id"])
        property_company_ids = set(
            self.properties_df["company_id"]
        )

        self.assertTrue(
            property_company_ids.issubset(company_ids)
        )

    def test_invalid_platform_is_rejected(self):
        catalog = {
            "media_companies": [
                {
                    "company_id": "MC001",
                    "company_name": "Test Media",
                    "properties": [
                        {
                            "property_id": "MP001",
                            "property_name": "Test Property",
                            "property_type": "Test Network",
                            "platform": "Invalid Platform",
                        }
                    ],
                }
            ]
        }

        with self.assertRaisesRegex(
            ValueError,
            "Invalid platform values",
        ):
            build_media_reference_frames(catalog)

    def test_content_catalog_builds_expected_counts(self):
        content_catalog = load_content_catalog(
            Path("config/v2_content_catalog.json")
        )

        programs_df, bridge_df = (
            build_content_reference_frames(
                content_catalog,
                self.companies_df,
                self.properties_df,
            )
        )

        self.assertEqual(len(programs_df), 12)
        self.assertEqual(len(bridge_df), 26)

    def test_bridge_property_ids_are_valid(self):
        content_catalog = load_content_catalog(
            Path("config/v2_content_catalog.json")
        )

        _, bridge_df = build_content_reference_frames(
            content_catalog,
            self.companies_df,
            self.properties_df,
        )

        valid_property_ids = set(
            self.properties_df["property_id"]
        )
        bridge_property_ids = set(bridge_df["property_id"])

        self.assertTrue(
            bridge_property_ids.issubset(valid_property_ids)
        )

    def test_unknown_distribution_property_is_rejected(self):
        content_catalog = {
            "programs": [
                {
                    "program_id": "PG001",
                    "program_name": "Test Program",
                    "genre": "Drama",
                    "content_owner_company_id": "MC001",
                    "distribution_property_ids": ["MP999"],
                }
            ]
        }

        with self.assertRaisesRegex(
            ValueError,
            "unknown media properties",
        ):
            build_content_reference_frames(
                content_catalog,
                self.companies_df,
                self.properties_df,
            )


if __name__ == "__main__":
    unittest.main()