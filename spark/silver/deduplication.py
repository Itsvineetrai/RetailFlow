"""
Deduplication utilities.
"""

from pyspark.sql import DataFrame


def remove_duplicates(
    df: DataFrame,
) -> DataFrame:

    return (

        df.dropDuplicates(
            [
                "transaction_id",
            ]
        )

    )