import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.v2_generator.output import write_csv_table


class TestOutputWriter(unittest.TestCase):

    def test_dataframe_is_written_without_index(self):
        dataframe = pd.DataFrame(
            {
                "company_id": ["MC001", "MC002"],
                "company_name": [
                    "Test Media One",
                    "Test Media Two",
                ],
            }
        )

        with tempfile.TemporaryDirectory() as temp_directory:
            output_path = (
                Path(temp_directory) / "media_company.csv"
            )

            returned_path = write_csv_table(
                dataframe,
                output_path,
            )

            written_dataframe = pd.read_csv(output_path)

            self.assertEqual(returned_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertEqual(
                list(written_dataframe.columns),
                ["company_id", "company_name"],
            )
            self.assertEqual(len(written_dataframe), 2)

    def test_empty_dataframe_is_rejected(self):
        dataframe = pd.DataFrame()

        with tempfile.TemporaryDirectory() as temp_directory:
            output_path = (
                Path(temp_directory) / "empty.csv"
            )

            with self.assertRaisesRegex(
                ValueError,
                "Cannot write an empty table",
            ):
                write_csv_table(
                    dataframe,
                    output_path,
                )


if __name__ == "__main__":
    unittest.main()