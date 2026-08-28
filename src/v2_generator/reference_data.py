import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_media_catalog(catalog_path: Path) -> dict[str, Any]:
    with catalog_path.open("r", encoding="utf-8") as catalog_file:
        return json.load(catalog_file)


def validate_media_reference_frames(
    companies_df: pd.DataFrame,
    properties_df: pd.DataFrame,
) -> None:
    valid_platforms = {"Linear TV", "Streaming"}

    if companies_df.empty:
        raise ValueError("The media-company catalog cannot be empty.")

    if properties_df.empty:
        raise ValueError("The media-property catalog cannot be empty.")

    if companies_df["company_id"].duplicated().any():
        raise ValueError("Duplicate company_id values were found.")

    if properties_df["property_id"].duplicated().any():
        raise ValueError("Duplicate property_id values were found.")

    company_ids = set(companies_df["company_id"])
    property_company_ids = set(properties_df["company_id"])

    orphan_company_ids = property_company_ids - company_ids
    if orphan_company_ids:
        raise ValueError(
            f"Properties reference unknown companies: "
            f"{sorted(orphan_company_ids)}"
        )

    companies_without_properties = company_ids - property_company_ids
    if companies_without_properties:
        raise ValueError(
            f"Companies have no media properties: "
            f"{sorted(companies_without_properties)}"
        )

    invalid_platforms = set(properties_df["platform"]) - valid_platforms
    if invalid_platforms:
        raise ValueError(
            f"Invalid platform values: {sorted(invalid_platforms)}"
        )


def build_media_reference_frames(
    catalog: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    company_records = []
    property_records = []

    for company in catalog["media_companies"]:
        company_records.append(
            {
                "company_id": company["company_id"],
                "company_name": company["company_name"],
            }
        )

        for media_property in company["properties"]:
            property_records.append(
                {
                    "property_id": media_property["property_id"],
                    "property_name": media_property["property_name"],
                    "property_type": media_property["property_type"],
                    "platform": media_property["platform"],
                    "company_id": company["company_id"],
                }
            )

    companies_df = pd.DataFrame(company_records)
    properties_df = pd.DataFrame(property_records)

    validate_media_reference_frames(companies_df, properties_df)

    return companies_df, properties_df


def load_content_catalog(catalog_path: Path) -> dict[str, Any]:
    with catalog_path.open("r", encoding="utf-8") as catalog_file:
        return json.load(catalog_file)


def validate_content_reference_frames(
    programs_df: pd.DataFrame,
    program_property_bridge_df: pd.DataFrame,
    companies_df: pd.DataFrame,
    properties_df: pd.DataFrame,
) -> None:
    if programs_df.empty:
        raise ValueError("The program catalog cannot be empty.")

    if program_property_bridge_df.empty:
        raise ValueError(
            "The program-property bridge cannot be empty."
        )

    if programs_df["program_id"].duplicated().any():
        raise ValueError("Duplicate program_id values were found.")

    duplicate_bridge_rows = program_property_bridge_df.duplicated(
        subset=["program_id", "property_id"]
    )

    if duplicate_bridge_rows.any():
        raise ValueError(
            "Duplicate program-property relationships were found."
        )

    valid_company_ids = set(companies_df["company_id"])
    owner_company_ids = set(
        programs_df["content_owner_company_id"]
    )

    invalid_owner_ids = owner_company_ids - valid_company_ids
    if invalid_owner_ids:
        raise ValueError(
            f"Programs reference unknown owner companies: "
            f"{sorted(invalid_owner_ids)}"
        )

    valid_property_ids = set(properties_df["property_id"])
    distributed_property_ids = set(
        program_property_bridge_df["property_id"]
    )

    invalid_property_ids = (
        distributed_property_ids - valid_property_ids
    )

    if invalid_property_ids:
        raise ValueError(
            f"Programs reference unknown media properties: "
            f"{sorted(invalid_property_ids)}"
        )

    program_ids = set(programs_df["program_id"])
    distributed_program_ids = set(
        program_property_bridge_df["program_id"]
    )

    programs_without_distribution = (
        program_ids - distributed_program_ids
    )

    if programs_without_distribution:
        raise ValueError(
            f"Programs have no distribution properties: "
            f"{sorted(programs_without_distribution)}"
        )


def build_content_reference_frames(
    catalog: dict[str, Any],
    companies_df: pd.DataFrame,
    properties_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    program_records = []
    bridge_records = []

    for program in catalog["programs"]:
        program_records.append(
            {
                "program_id": program["program_id"],
                "program_name": program["program_name"],
                "genre": program["genre"],
                "content_owner_company_id": (
                    program["content_owner_company_id"]
                ),
            }
        )

        for property_id in program["distribution_property_ids"]:
            bridge_records.append(
                {
                    "program_id": program["program_id"],
                    "property_id": property_id,
                }
            )

    programs_df = pd.DataFrame(program_records)
    program_property_bridge_df = pd.DataFrame(bridge_records)

    validate_content_reference_frames(
        programs_df=programs_df,
        program_property_bridge_df=program_property_bridge_df,
        companies_df=companies_df,
        properties_df=properties_df,
    )

    return programs_df, program_property_bridge_df