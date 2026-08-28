from pathlib import Path

import pandas as pd


def write_csv_table(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> Path:
    if dataframe.empty:
        raise ValueError(
            f"Cannot write an empty table to {output_path}."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    return output_path