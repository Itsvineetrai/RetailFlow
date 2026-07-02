"""
Write POS transactions to a temporary CSV file.
"""

from __future__ import annotations

from dataclasses import asdict
import csv
from pathlib import Path
from core.config import get_config
from core.models.transaction import Transaction


config = get_config()


class CSVWriter:

    def __init__(self):

        self.output_directory = Path(
            config.get(
                "storage",
                "temp",
            )
        )

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def write(
        self,
        transactions: list[Transaction],
        filename: str,
    ) -> Path:

        filepath = self.output_directory / filename

        with filepath.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=asdict(transactions[0]).keys(),
            )

            writer.writeheader()

            for transaction in transactions:
                writer.writerow(
                    asdict(transaction)
                )

        return filepath