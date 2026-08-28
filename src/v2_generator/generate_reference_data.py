from pathlib import Path

from src.v2_generator.advertiser_data import (
    build_advertiser_frame,
    load_advertiser_catalog,
)
from src.v2_generator.config import load_config
from src.v2_generator.output import write_csv_table
from src.v2_generator.reference_data import (
    build_content_reference_frames,
    build_media_reference_frames,
    load_content_catalog,
    load_media_catalog,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    generator_config = load_config(
        PROJECT_ROOT / "config" / "v2_generator_config.json"
    )

    media_catalog = load_media_catalog(
        PROJECT_ROOT / "config" / "v2_media_catalog.json"
    )

    content_catalog = load_content_catalog(
        PROJECT_ROOT / "config" / "v2_content_catalog.json"
    )

    advertiser_catalog = load_advertiser_catalog(
        PROJECT_ROOT / "config" / "v2_advertiser_catalog.json"
    )

    companies_df, properties_df = (
        build_media_reference_frames(media_catalog)
    )

    programs_df, program_property_bridge_df = (
        build_content_reference_frames(
            content_catalog,
            companies_df,
            properties_df,
        )
    )

    advertisers_df = build_advertiser_frame(
        advertiser_catalog
    )

    output_directory = (
        PROJECT_ROOT / generator_config.output_directory
    )

    tables = {
    "media_company.csv": companies_df,
    "media_property.csv": properties_df,
    "program.csv": programs_df,
    "bridge_program_property.csv": program_property_bridge_df,
    "advertiser.csv": advertisers_df,
    }

    for file_name, dataframe in tables.items():
        output_path = write_csv_table(
            dataframe,
            output_directory / file_name,
        )

        print(
            f"Wrote {len(dataframe):,} rows to "
            f"{output_path.relative_to(PROJECT_ROOT)}"
        )


if __name__ == "__main__":
    main()