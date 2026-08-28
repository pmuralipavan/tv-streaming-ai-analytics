import unittest
from pathlib import Path

from src.v2_generator.market_behavior import (
    build_platform_trend_frame,
    compound_value,
)
from src.v2_generator.market_rules import load_market_rules


class TestMarketBehavior(unittest.TestCase):

    def setUp(self):
        self.rules = load_market_rules(
            Path("config/v2_market_rules.json")
        )

    def test_compound_value(self):
        result = compound_value(
            base_value=100,
            annual_rate=0.04,
            periods=4,
        )

        self.assertAlmostEqual(result, 116.985856)

    def test_base_year_indexes_equal_one_hundred(self):
        trends_df = build_platform_trend_frame(
            self.rules,
            start_year=2022,
            end_year=2022,
        )

        self.assertTrue(
            (trends_df["demand_index"] == 100).all()
        )

        self.assertTrue(
            (trends_df["inventory_index"] == 100).all()
        )

        self.assertTrue(
            (
                trends_df["sell_through_pressure_index"]
                == 100
            ).all()
        )

    def test_2026_platform_directions(self):
        trends_df = build_platform_trend_frame(
            self.rules,
            start_year=2022,
            end_year=2026,
        )

        results_2026 = trends_df[
            trends_df["year"] == 2026
        ].set_index("platform")

        self.assertGreater(
            results_2026.loc["Streaming", "demand_index"],
            100,
        )

        self.assertLess(
            results_2026.loc["Linear TV", "demand_index"],
            100,
        )

        self.assertGreater(
            results_2026.loc[
                "Streaming",
                "sell_through_pressure_index",
            ],
            100,
        )

        self.assertLess(
            results_2026.loc[
                "Linear TV",
                "sell_through_pressure_index",
            ],
            100,
        )

    def test_streaming_cpm_overtakes_linear(self):
        trends_df = build_platform_trend_frame(
            self.rules,
            start_year=2022,
            end_year=2026,
        )

        cpm_by_year = trends_df.pivot(
            index="year",
            columns="platform",
            values="projected_base_cpm",
        )

        self.assertGreater(
            cpm_by_year.loc[2022, "Linear TV"],
            cpm_by_year.loc[2022, "Streaming"],
        )

        self.assertLess(
            cpm_by_year.loc[2026, "Linear TV"],
            cpm_by_year.loc[2026, "Streaming"],
        )

        self.assertLess(
            cpm_by_year.loc[2026, "Linear TV"],
            cpm_by_year.loc[2022, "Linear TV"],
        )

        self.assertGreater(
            cpm_by_year.loc[2026, "Streaming"],
            cpm_by_year.loc[2022, "Streaming"],
        )

        crossover_years = cpm_by_year.index[
            cpm_by_year["Streaming"]
            > cpm_by_year["Linear TV"]
        ].tolist()

        self.assertTrue(crossover_years)
        self.assertGreaterEqual(crossover_years[0], 2024)
        self.assertLessEqual(crossover_years[0], 2026)

    def test_end_year_before_start_year_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "end_year cannot be earlier than start_year",
        ):
            build_platform_trend_frame(
                self.rules,
                start_year=2026,
                end_year=2022,
            )


if __name__ == "__main__":
    unittest.main()