import json
from pathlib import Path
from typing import Any


EXPECTED_PLATFORMS = {"Linear TV", "Streaming"}
EXPECTED_MONTHS = {str(month) for month in range(1, 13)}

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