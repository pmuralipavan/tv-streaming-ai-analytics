import unittest
from datetime import date
from pathlib import Path

from src.v2_generator.config import (
    GeneratorConfig,
    load_config,
    validate_config,
)


class TestGeneratorConfig(unittest.TestCase):

    def test_valid_json_config_loads(self):
        config_path = Path("config/v2_generator_config.json")

        config = load_config(config_path)

        self.assertEqual(config.dataset_tier, "development")
        self.assertEqual(config.ad_delivery_row_count, 50000)
        self.assertEqual(config.start_date, date(2022, 1, 1))
        self.assertEqual(config.end_date, date(2026, 6, 30))

    def test_zero_row_count_is_rejected(self):
        config = GeneratorConfig(
            dataset_version="2.0",
            dataset_tier="development",
            market_scope="United States",
            ad_delivery_row_count=0,
            start_date=date(2022, 1, 1),
            end_date=date(2026, 6, 30),
            random_seed=42,
            quality_exception_rate=0.0075,
            output_directory=Path("data/v2/generated"),
            output_format="csv",
        )

        with self.assertRaisesRegex(
            ValueError,
            "ad_delivery_row_count must be greater than zero",
        ):
            validate_config(config)


if __name__ == "__main__":
    unittest.main()