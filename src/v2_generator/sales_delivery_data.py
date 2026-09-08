import numpy as np
import pandas as pd
from src.v2_generator.market_behavior import BASE_YEAR


def validate_sales_delivery_frame(
    sales_delivery_df: pd.DataFrame,
) -> None:
    if sales_delivery_df.empty:
        raise ValueError(
            "Generated sales and delivery data cannot be empty."
        )

    if sales_delivery_df["sales_delivery_id"].duplicated().any():
        raise ValueError(
            "Duplicate sales_delivery_id values were generated."
        )

    if sales_delivery_df["inventory_id"].isnull().any():
        raise ValueError(
            "inventory_id cannot be null."
        )

    if (
        sales_delivery_df["sold_inventory_units"] < 0
    ).any():
        raise ValueError(
            "Sold inventory units cannot be negative."
        )

    if (
        sales_delivery_df["booked_impressions"] < 0
    ).any():
        raise ValueError(
            "Booked impressions cannot be negative."
        )

    if (
        sales_delivery_df["delivered_impressions"] < 0
    ).any():
        raise ValueError(
            "Delivered impressions cannot be negative."
        )
    if (
        sales_delivery_df["gross_revenue"] < 0
    ).any():
        raise ValueError(
            "Gross revenue cannot be negative."
        )

    if (
        sales_delivery_df["net_revenue"] < 0
    ).any():
        raise ValueError(
            "Net revenue cannot be negative."
        )
        

def generate_sales_delivery(
    inventory_df: pd.DataFrame,
    random_seed: int,
    market_rules: dict,
    properties_df: pd.DataFrame,
    programs_df: pd.DataFrame,
) -> pd.DataFrame:
    if inventory_df.empty:
        raise ValueError(
            "Inventory data cannot be empty."
        )

    sales_rules = market_rules[
        "sales_delivery_generation"
    ]

    sales_delivery_df = inventory_df.merge(
        properties_df[
            [
                "property_id",
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
    
    sales_delivery_df["year_offset"] = (
        sales_delivery_df["inventory_month"].dt.year
        - BASE_YEAR
    )

    base_cpm_by_platform = {
        platform: rules["base_cpm_2022"]
        for platform, rules in market_rules[
            "platform_rules"
        ].items()
    }

    annual_cpm_growth_by_platform = {
        platform: rules["annual_cpm_growth_rate"]
        for platform, rules in market_rules[
            "platform_rules"
        ].items()
    }

    sales_delivery_df["base_cpm"] = (
        sales_delivery_df["platform"].map(
            base_cpm_by_platform
        )
    )

    sales_delivery_df["annual_cpm_growth_rate"] = (
        sales_delivery_df["platform"].map(
            annual_cpm_growth_by_platform
        )
    )

    sales_delivery_df["genre_cpm_multiplier"] = (
        sales_delivery_df["genre"].map(
            market_rules["genre_cpm_multipliers"]
        )
    )

    sales_delivery_df["daypart_cpm_multiplier"] = (
        sales_delivery_df["daypart"].map(
            market_rules["daypart_cpm_multipliers"]
        )
    )

    sales_delivery_df["effective_cpm"] = (
        sales_delivery_df["base_cpm"]
        * (
            (
                1
                + sales_delivery_df[
                    "annual_cpm_growth_rate"
                ]
            )
            ** sales_delivery_df["year_offset"]
        )
        * sales_delivery_df["genre_cpm_multiplier"]
        * sales_delivery_df["daypart_cpm_multiplier"]
    )
    

    base_sell_through_rates = sales_rules[
        "base_sell_through_rate_by_platform"
    ]

    sales_delivery_df["base_sell_through_rate"] = (
        sales_delivery_df["platform"].map(
            base_sell_through_rates
        )
    )

    random_generator = np.random.default_rng(
        random_seed
    )

    sales_delivery_df["sell_through_rate"] = (
        sales_delivery_df["base_sell_through_rate"]
        * random_generator.uniform(
            low=0.90,
            high=1.10,
            size=len(sales_delivery_df),
        )
    )

    sales_delivery_df["sell_through_rate"] = (
        sales_delivery_df["sell_through_rate"].clip(
            lower=sales_rules[
                "minimum_sell_through_rate"
            ],
            upper=sales_rules[
                "maximum_sell_through_rate"
            ],
        )
    )

    sales_delivery_df["sold_inventory_units"] = (
        (
            sales_delivery_df["available_inventory_units"]
            * sales_delivery_df["sell_through_rate"]
        )
        .round()
        .astype(int)
    )

    sales_delivery_df["booked_impressions"] = (
        sales_delivery_df["sold_inventory_units"]
        * sales_rules["impressions_per_inventory_unit"]
    )

    delivery_rate_means = {
        platform: rules["delivery_rate_mean"]
        for platform, rules in market_rules[
            "platform_rules"
        ].items()
    }

    delivery_rate_standard_deviations = {
        platform: rules[
            "delivery_rate_standard_deviation"
        ]
        for platform, rules in market_rules[
            "platform_rules"
        ].items()
    }

    sales_delivery_df["delivery_rate_mean"] = (
        sales_delivery_df["platform"].map(
            delivery_rate_means
        )
    )

    sales_delivery_df[
        "delivery_rate_standard_deviation"
    ] = sales_delivery_df["platform"].map(
        delivery_rate_standard_deviations
    )

    sales_delivery_df["delivery_rate"] = (
        random_generator.normal(
            loc=sales_delivery_df["delivery_rate_mean"],
            scale=sales_delivery_df[
                "delivery_rate_standard_deviation"
            ],
        )
    )

    sales_delivery_df["delivery_rate"] = (
        sales_delivery_df["delivery_rate"].clip(
            lower=sales_rules[
                "minimum_delivery_rate"
            ],
            upper=sales_rules[
                "maximum_delivery_rate"
            ],
        )
    )

    booked_impressions = sales_delivery_df[
        "booked_impressions"
    ].to_numpy()

    delivery_rates = sales_delivery_df[
        "delivery_rate"
    ].to_numpy()

    sales_delivery_df["delivered_impressions"] = (
        np.rint(
            booked_impressions * delivery_rates
        ).astype(int)
    )

    sales_delivery_df["gross_revenue"] = (
    sales_delivery_df["delivered_impressions"]
    / 1000
    * sales_delivery_df["effective_cpm"]
    )

    sales_delivery_df["agency_fee"] = (
        sales_delivery_df["gross_revenue"]
        * sales_rules["agency_fee_rate"]
    )

    sales_delivery_df["net_revenue"] = (
        sales_delivery_df["gross_revenue"]
        - sales_delivery_df["agency_fee"]
    )

    return sales_delivery_df