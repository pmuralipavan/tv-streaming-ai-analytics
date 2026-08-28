import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class GeneratorConfig:
    dataset_version: str
    dataset_tier: str
    market_scope: str
    ad_delivery_row_count: int
    start_date: date
    end_date: date
    random_seed: int
    quality_exception_rate: float
    output_directory: Path
    output_format: str


def validate_config(config: GeneratorConfig) -> None:
    valid_tiers = {"development", "portfolio", "scale"}
    valid_formats = {"csv", "parquet"}

    if config.dataset_tier not in valid_tiers:
        raise ValueError(
            f"dataset_tier must be one of {valid_tiers}."
        )

    if config.ad_delivery_row_count <= 0:
        raise ValueError(
            "ad_delivery_row_count must be greater than zero."
        )

    if config.start_date >= config.end_date:
        raise ValueError(
            "start_date must be earlier than end_date."
        )

    if not 0 <= config.quality_exception_rate <= 0.05:
        raise ValueError(
            "quality_exception_rate must be between 0 and 0.05."
        )

    if config.output_format not in valid_formats:
        raise ValueError(
            f"output_format must be one of {valid_formats}."
        )


def load_config(config_path: Path) -> GeneratorConfig:
    with config_path.open("r", encoding="utf-8") as config_file:
        raw_config = json.load(config_file)

    config = GeneratorConfig(
        dataset_version=raw_config["dataset_version"],
        dataset_tier=raw_config["dataset_tier"],
        market_scope=raw_config["market_scope"],
        ad_delivery_row_count=raw_config["ad_delivery_row_count"],
        start_date=date.fromisoformat(raw_config["start_date"]),
        end_date=date.fromisoformat(raw_config["end_date"]),
        random_seed=raw_config["random_seed"],
        quality_exception_rate=raw_config["quality_exception_rate"],
        output_directory=Path(raw_config["output_directory"]),
        output_format=raw_config["output_format"],
    )

    validate_config(config)
    return config