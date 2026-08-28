import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_advertiser_catalog(
    catalog_path: Path,
) -> dict[str, Any]:
    with catalog_path.open("r", encoding="utf-8") as catalog_file:
        return json.load(catalog_file)


def validate_advertisers(advertisers_df: pd.DataFrame) -> None:
    required_columns = {
        "advertiser_id",
        "advertiser_name",
        "industry",
        "size_tier",
        "platform_strategy",
        "budget_weight",
    }

    valid_size_tiers = {"Enterprise", "Growth"}
    valid_platform_strategies = {
        "Linear First",
        "Streaming First",
        "Balanced",
    }

    missing_columns = required_columns - set(advertisers_df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing advertiser columns: {sorted(missing_columns)}"
        )

    if advertisers_df.empty:
        raise ValueError("The advertiser catalog cannot be empty.")

    if advertisers_df[list(required_columns)].isnull().any().any():
        raise ValueError(
            "Advertiser records cannot contain null values."
        )

    if advertisers_df["advertiser_id"].duplicated().any():
        raise ValueError("Duplicate advertiser_id values were found.")

    invalid_size_tiers = (
        set(advertisers_df["size_tier"]) - valid_size_tiers
    )

    if invalid_size_tiers:
        raise ValueError(
            f"Invalid advertiser size tiers: "
            f"{sorted(invalid_size_tiers)}"
        )

    invalid_strategies = (
        set(advertisers_df["platform_strategy"])
        - valid_platform_strategies
    )

    if invalid_strategies:
        raise ValueError(
            f"Invalid platform strategies: "
            f"{sorted(invalid_strategies)}"
        )

    if not pd.api.types.is_numeric_dtype(
        advertisers_df["budget_weight"]
    ):
        raise ValueError("budget_weight must be numeric.")

    if (advertisers_df["budget_weight"] <= 0).any():
        raise ValueError(
            "budget_weight must be greater than zero."
        )


def build_advertiser_frame(
    catalog: dict[str, Any],
) -> pd.DataFrame:
    advertisers_df = pd.DataFrame(catalog["advertisers"])

    validate_advertisers(advertisers_df)

    return advertisers_df