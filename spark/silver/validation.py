"""
Validation rules for Silver Layer.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col


def validate_transactions(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """
    Split the dataframe into valid and invalid records.
    """

    valid_df = (

        df

        .filter(col("transaction_id").isNotNull())

        .filter(col("customer_id").isNotNull())

        .filter(col("product_id").isNotNull())

        .filter(col("amount") > 0)

        .filter(col("quantity") > 0)

    )

    invalid_df = df.subtract(valid_df)

    return valid_df, invalid_df