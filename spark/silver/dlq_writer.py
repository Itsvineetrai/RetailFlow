"""
Dead Letter Queue writer.
"""

from pyspark.sql import DataFrame

from core.config import get_config

config = get_config()


def write_dlq(
    df: DataFrame,
):

    (

        df.write

        .format("delta")

        .mode("append")

        .save(

            config.get(
                "storage",
                "dlq",
            )

        )

    )