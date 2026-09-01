from datetime import date

import numpy as np
import pandas as pd

from src.v2_generator.market_behavior import BASE_YEAR


def validate_inventory_frame(
    inventory_df: pd.DataFrame,
    minimum_inventory_units: int,
) -> None:
    grain_columns = [
        "inventory_month",
        "property_id",
        "program_id",
        "daypart",
    ]

    if inventory_df.empty:
        raise ValueError("Generated inventory cannot be empty.")

    if inventory_df.duplicated(
        subset=grain_columns
    ).any():
        raise ValueError(
            "Duplicate rows were generated at the inventory grain."
        )

    if inventory_df["inventory_id"].duplicated().any():
        raise ValueError(
            "Duplicate inventory_id values were generated."
        )

    if inventory_df["available_inventory_units"].isnull().any():
        raise ValueError(
            "Available inventory units cannot be null."
        )

    if (
        inventory_df["available_inventory_units"]
        < minimum_inventory_units
    ).any():
        raise ValueError(
            "Available inventory units fell below the minimum."
        )


def generate_inventory(
    start_date: date,
    end_date: date,
    random_seed: int,
    market_rules: dict,
    properties_df: pd.DataFrame,
    programs_df: pd.DataFrame,
    program_property_bridge_df: pd.DataFrame,
) -> pd.DataFrame:
    if end_date < start_date:
        raise ValueError(
            "Inventory end_date cannot be earlier than start_date."
        )

    inventory_rules = market_rules["inventory_generation"]

    valid_placements = program_property_bridge_df.merge(
        properties_df[
            [
                "property_id",
                "property_type",
                "platform",
            ]
        ],
        on="property_id",
        how="inner",
        validate="many_to_one",
    ).merge(
        programs_df[
            [
                "program_id",
                "genre",
            ]
        ],
        on="program_id",
        how="inner",
        validate="many_to_one",
    )

    months_df = pd.DataFrame(
        {
            "inventory_month": pd.date_range(
                start=start_date,
                end=end_date,
                freq="MS",
            )
        }
    )

    schedule_records = []

    genre_daypart_rules = inventory_rules[
        "genre_daypart_weights_by_platform"
    ]

    for platform, genre_rules in (
        genre_daypart_rules.items()
    ):
        for genre, daypart_weights in genre_rules.items():
            for daypart, schedule_weight in (
                daypart_weights.items()
            ):
                schedule_records.append(
                    {
                        "platform": platform,
                        "genre": genre,
                        "daypart": daypart,
                        "schedule_weight": schedule_weight,
                    }
                )

    schedule_df = pd.DataFrame(schedule_records)

    eligible_placements = valid_placements.merge(
        schedule_df,
        on=["platform", "genre"],
        how="inner",
        validate="many_to_many",
    )

    inventory_df = months_df.merge(
        eligible_placements,
        how="cross",
    )

    inventory_df["year_offset"] = (
        inventory_df["inventory_month"].dt.year
        - BASE_YEAR
    )

    base_units_by_property_type = inventory_rules[
        "base_monthly_units_by_property_type"
    ]

    annual_growth_by_platform = {
        platform: platform_rule[
            "annual_inventory_growth_rate"
        ]
        for platform, platform_rule
        in market_rules["platform_rules"].items()
    }

    monthly_inventory_multipliers = {
        int(month): multiplier
        for month, multiplier
        in market_rules[
            "monthly_inventory_multipliers"
        ].items()
    }

    inventory_df["base_units"] = inventory_df[
        "property_type"
    ].map(base_units_by_property_type)

    inventory_df["annual_growth_rate"] = inventory_df[
        "platform"
    ].map(annual_growth_by_platform)

    inventory_df["monthly_multiplier"] = (
        inventory_df["inventory_month"].dt.month.map(
            monthly_inventory_multipliers
        )
    )

    inventory_df["daypart_multiplier"] = inventory_df[
        "daypart"
    ].map(
        inventory_rules["daypart_supply_multipliers"]
    )

    random_generator = np.random.default_rng(random_seed)

    inventory_df["random_variation"] = (
        random_generator.uniform(
            low=inventory_rules[
                "random_variation_minimum"
            ],
            high=inventory_rules[
                "random_variation_maximum"
            ],
            size=len(inventory_df),
        )
    )

    calculated_units = (
        inventory_df["base_units"]
        * (
            (1 + inventory_df["annual_growth_rate"])
            ** inventory_df["year_offset"]
        )
        * inventory_df["monthly_multiplier"]
        * inventory_df["daypart_multiplier"]
        * inventory_df["schedule_weight"]
        * inventory_df["random_variation"]
    )

    minimum_units = inventory_rules[
        "minimum_inventory_units"
    ]

    inventory_df["available_inventory_units"] = (
        calculated_units
        .round()
        .astype(int)
        .clip(lower=minimum_units)
    )

    inventory_df = inventory_df.sort_values(
        by=[
            "inventory_month",
            "property_id",
            "program_id",
            "daypart",
        ]
    ).reset_index(drop=True)

    inventory_df["inventory_id"] = [
        f"INV{row_number:07d}"
        for row_number in range(1, len(inventory_df) + 1)
    ]

    final_inventory_df = inventory_df[
        [
            "inventory_id",
            "inventory_month",
            "property_id",
            "program_id",
            "daypart",
            "available_inventory_units",
        ]
    ].copy()

    validate_inventory_frame(
        final_inventory_df,
        minimum_inventory_units=minimum_units,
    )

    return final_inventory_df