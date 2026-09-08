import json
from pathlib import Path
from typing import Any


EXPECTED_PLATFORMS = {"Linear TV", "Streaming"}
EXPECTED_MONTHS = {str(month) for month in range(1, 13)}
EXPECTED_PROPERTY_TYPES = {
    "Broadcast Network",
    "Cable Network",
    "Streaming Service",
}

EXPECTED_DAYPARTS = {
    "Morning",
    "Daytime",
    "Early Fringe",
    "Primetime",
    "Late Night",
    "Live Event",
}
EXPECTED_GENRES = {
    "Sports",
    "Crime Drama",
    "Drama",
    "News",
    "Comedy",
    "Reality",
    "Talk",
    "Documentary",
    "Lifestyle",
}

REQUIRED_PLATFORM_FIELDS = {
    "base_cpm_2022",
    "annual_cpm_growth_rate",
    "annual_demand_growth_rate",
    "annual_inventory_growth_rate",
    "delivery_rate_mean",
    "delivery_rate_standard_deviation",
}


def load_market_rules(
    rules_path: Path,
) -> dict[str, Any]:
    with rules_path.open("r", encoding="utf-8") as rules_file:
        rules = json.load(rules_file)

    validate_market_rules(rules)

    return rules


def validate_market_rules(rules: dict[str, Any]) -> None:
    platform_rules = rules.get("platform_rules", {})

    if set(platform_rules) != EXPECTED_PLATFORMS:
        raise ValueError(
            "Platform rules must define Linear TV and Streaming."
        )

    for platform, platform_rule in platform_rules.items():
        missing_fields = (
            REQUIRED_PLATFORM_FIELDS - set(platform_rule)
        )

        if missing_fields:
            raise ValueError(
                f"{platform} is missing fields: "
                f"{sorted(missing_fields)}"
            )

        if platform_rule["base_cpm_2022"] <= 0:
            raise ValueError(
                f"{platform} base CPM must be greater than zero."
            )

        for rate_name in (
            "annual_cpm_growth_rate",
            "annual_demand_growth_rate",
            "annual_inventory_growth_rate",
        ):
            rate = platform_rule[rate_name]

            if not -0.2 <= rate <= 0.2:
                raise ValueError(
                    f"{platform} {rate_name} must be between "
                    f"-0.20 and 0.20."
                )

        delivery_mean = platform_rule["delivery_rate_mean"]
        if not 0 < delivery_mean <= 1:
            raise ValueError(
                f"{platform} delivery_rate_mean must be "
                f"greater than 0 and no more than 1."
            )

        delivery_deviation = platform_rule[
            "delivery_rate_standard_deviation"
        ]

        if not 0 <= delivery_deviation <= 0.25:
            raise ValueError(
                f"{platform} delivery-rate deviation must be "
                f"between 0 and 0.25."
            )

    platform_weights = rules.get(
        "advertiser_platform_weights",
        {},
    )

    if not platform_weights:
        raise ValueError(
            "Advertiser platform weights cannot be empty."
        )

    for strategy, weights in platform_weights.items():
        if set(weights) != EXPECTED_PLATFORMS:
            raise ValueError(
                f"{strategy} must define weights for both platforms."
            )

        if any(weight < 0 for weight in weights.values()):
            raise ValueError(
                f"{strategy} contains a negative platform weight."
            )

        if abs(sum(weights.values()) - 1.0) > 0.000001:
            raise ValueError(
                f"{strategy} platform weights must total 1.0."
            )

    validate_monthly_multipliers(
        rules.get("monthly_demand_multipliers", {}),
        "monthly_demand_multipliers",
    )

    validate_monthly_multipliers(
        rules.get("monthly_inventory_multipliers", {}),
        "monthly_inventory_multipliers",
    )

    validate_positive_multipliers(
        rules.get("genre_cpm_multipliers", {}),
        "genre_cpm_multipliers",
    )

    validate_positive_multipliers(
        rules.get("daypart_cpm_multipliers", {}),
        "daypart_cpm_multipliers",
    )

    validate_inventory_generation(
        rules.get("inventory_generation", {})
    )

    validate_sales_delivery_generation(
        rules.get("sales_delivery_generation", {})
    )


def validate_monthly_multipliers(
    multipliers: dict[str, float],
    rule_name: str,
) -> None:
    if set(multipliers) != EXPECTED_MONTHS:
        raise ValueError(
            f"{rule_name} must contain months 1 through 12."
        )

    validate_positive_multipliers(
        multipliers,
        rule_name,
    )


def validate_positive_multipliers(
    multipliers: dict[str, float],
    rule_name: str,
) -> None:
    if not multipliers:
        raise ValueError(f"{rule_name} cannot be empty.")

    if any(value <= 0 for value in multipliers.values()):
        raise ValueError(
            f"{rule_name} values must be greater than zero."
        )

def validate_inventory_generation(
    inventory_rules: dict[str, Any],
) -> None:
    required_fields = {
        "base_monthly_units_by_property_type",
        "daypart_supply_multipliers",
        "genre_daypart_weights_by_platform",
        "random_variation_minimum",
        "random_variation_maximum",
        "minimum_inventory_units",
    }

    missing_fields = required_fields - set(inventory_rules)
    if missing_fields:
        raise ValueError(
            f"Inventory generation is missing fields: "
            f"{sorted(missing_fields)}"
        )

    base_units = inventory_rules[
        "base_monthly_units_by_property_type"
    ]

    if set(base_units) != EXPECTED_PROPERTY_TYPES:
        raise ValueError(
            "Inventory base units must define all property types."
        )

    if any(value <= 0 for value in base_units.values()):
        raise ValueError(
            "Inventory base units must be greater than zero."
        )

    daypart_multipliers = inventory_rules[
        "daypart_supply_multipliers"
    ]

    if set(daypart_multipliers) != EXPECTED_DAYPARTS:
        raise ValueError(
            "Inventory supply multipliers must define all dayparts."
        )

    if any(
        value <= 0
        for value in daypart_multipliers.values()
    ):
        raise ValueError(
            "Inventory supply multipliers must be greater than zero."
        )

    genre_daypart_rules = inventory_rules[
        "genre_daypart_weights_by_platform"
    ]

    if set(genre_daypart_rules) != EXPECTED_PLATFORMS:
        raise ValueError(
            "Genre-daypart rules must define both platforms."
        )

    for platform, genre_rules in genre_daypart_rules.items():
        if set(genre_rules) != EXPECTED_GENRES:
            raise ValueError(
                f"{platform} must define all expected genres."
            )

        for genre, daypart_weights in genre_rules.items():
            if not daypart_weights:
                raise ValueError(
                    f"{platform} {genre} daypart weights "
                    f"cannot be empty."
                )

            invalid_dayparts = (
                set(daypart_weights) - EXPECTED_DAYPARTS
            )

            if invalid_dayparts:
                raise ValueError(
                    f"{platform} {genre} contains invalid "
                    f"dayparts: {sorted(invalid_dayparts)}"
                )

            if any(
                weight <= 0
                for weight in daypart_weights.values()
            ):
                raise ValueError(
                    f"{platform} {genre} daypart weights "
                    f"must be greater than zero."
                )

            if (
                abs(sum(daypart_weights.values()) - 1.0)
                > 0.000001
            ):
                raise ValueError(
                    f"{platform} {genre} daypart weights "
                    f"must total 1.0."
                )

    variation_minimum = inventory_rules[
        "random_variation_minimum"
    ]
    variation_maximum = inventory_rules[
        "random_variation_maximum"
    ]

    if not 0 < variation_minimum <= variation_maximum:
        raise ValueError(
            "Inventory variation minimum must be positive "
            "and no greater than the maximum."
        )

    minimum_units = inventory_rules[
        "minimum_inventory_units"
    ]

    if minimum_units <= 0:
        raise ValueError(
            "minimum_inventory_units must be greater than zero."
        )

def validate_sales_delivery_generation(
    sales_rules: dict[str, Any],
) -> None:
    required_fields = {
        "base_sell_through_rate_by_platform",
        "impressions_per_inventory_unit",
        "minimum_sell_through_rate",
        "maximum_sell_through_rate",
        "minimum_delivery_rate",
        "maximum_delivery_rate",
        "agency_fee_rate",
    }

    missing_fields = required_fields - set(sales_rules)

    if missing_fields:
        raise ValueError(
            "Sales delivery generation is missing fields: "
            f"{sorted(missing_fields)}"
        )

    sell_through_rates = sales_rules[
        "base_sell_through_rate_by_platform"
    ]

    if set(sell_through_rates) != EXPECTED_PLATFORMS:
        raise ValueError(
            "Sales delivery sell-through rates must define "
            "Linear TV and Streaming."
        )

    if any(
        not 0 < rate <= 1
        for rate in sell_through_rates.values()
    ):
        raise ValueError(
            "Base sell-through rates must be greater than 0 "
            "and no more than 1."
        )

    minimum_sell_through_rate = sales_rules[
        "minimum_sell_through_rate"
    ]

    maximum_sell_through_rate = sales_rules[
        "maximum_sell_through_rate"
    ]

    if not (
        0 < minimum_sell_through_rate
        <= maximum_sell_through_rate
        <= 1
    ):
        raise ValueError(
            "Sell-through bounds must be between 0 and 1."
        )

    minimum_delivery_rate = sales_rules[
        "minimum_delivery_rate"
    ]

    maximum_delivery_rate = sales_rules[
        "maximum_delivery_rate"
    ]

    if not (
        0 < minimum_delivery_rate
        <= maximum_delivery_rate
    ):
        raise ValueError(
            "Delivery-rate bounds must be positive "
            "and minimum cannot exceed maximum."
        )

    if sales_rules["impressions_per_inventory_unit"] <= 0:
        raise ValueError(
            "impressions_per_inventory_unit must be greater than zero."
        )

    agency_fee_rate = sales_rules["agency_fee_rate"]

    if not 0 <= agency_fee_rate < 1:
        raise ValueError(
            "agency_fee_rate must be between 0 and 1."
        )