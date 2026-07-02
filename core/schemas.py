"""
Shared Spark schemas for AeroMart.

All Spark jobs should use these schemas instead of
relying on inferSchema().
"""

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    BooleanType,
    TimestampType,
    DecimalType,
)

TRANSACTION_SCHEMA = StructType(
    [

        StructField(
            "transaction_id",
            StringType(),
            False,
        ),

        StructField(
            "transaction_timestamp",
            TimestampType(),
            False,
        ),

        StructField(
            "customer_id",
            StringType(),
            True,
        ),

        StructField(
            "product_id",
            StringType(),
            False,
        ),

        StructField(
            "store_id",
            StringType(),
            False,
        ),

        StructField(
            "country",
            StringType(),
            False,
        ),

        StructField(
            "currency",
            StringType(),
            False,
        ),

        StructField(
            "amount",
            DecimalType(18, 2),
            False,
        ),

        StructField(
            "quantity",
            IntegerType(),
            False,
        ),

        StructField(
            "payment_method",
            StringType(),
            False,
        ),

        StructField(
            "sales_channel",
            StringType(),
            False,
        ),

        StructField(
            "discount",
            DecimalType(18, 2),
            False,
        ),

        StructField(
            "tax",
            DecimalType(18, 2),
            False,
        ),

        StructField(
            "total_amount",
            DecimalType(18, 2),
            False,
        ),

        StructField(
            "is_return",
            BooleanType(),
            False,
        ),

        StructField(
            "ingestion_timestamp",
            TimestampType(),
            True,
        ),
    ]
)