import pandas as pd


BASE_YEAR = 2022
BASE_INDEX = 100.0


def compound_value(
    base_value: float,
    annual_rate: float,
    periods: int,
) -> float:
    return base_value * ((1 + annual_rate) ** periods)


def build_platform_trend_frame(
    market_rules: dict,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    if start_year < BASE_YEAR:
        raise ValueError(
            f"start_year cannot be earlier than {BASE_YEAR}."
        )

    if end_year < start_year:
        raise ValueError(
            "end_year cannot be earlier than start_year."
        )

    trend_records = []

    for year in range(start_year, end_year + 1):
        periods = year - BASE_YEAR

        for platform, rules in market_rules[
            "platform_rules"
        ].items():
            projected_cpm = compound_value(
                base_value=rules["base_cpm_2022"],
                annual_rate=rules["annual_cpm_growth_rate"],
                periods=periods,
            )

            demand_index = compound_value(
                base_value=BASE_INDEX,
                annual_rate=rules["annual_demand_growth_rate"],
                periods=periods,
            )

            inventory_index = compound_value(
                base_value=BASE_INDEX,
                annual_rate=rules[
                    "annual_inventory_growth_rate"
                ],
                periods=periods,
            )

            sell_through_pressure_index = (
                demand_index / inventory_index
            ) * BASE_INDEX

            trend_records.append(
                {
                    "year": year,
                    "platform": platform,
                    "projected_base_cpm": projected_cpm,
                    "demand_index": demand_index,
                    "inventory_index": inventory_index,
                    "sell_through_pressure_index": (
                        sell_through_pressure_index
                    ),
                }
            )

    return pd.DataFrame(trend_records)