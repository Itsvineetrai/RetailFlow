from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


class DailyDemandBuilder:

    @staticmethod
    def build(df: DataFrame) -> DataFrame:
        """
        Build daily store-product demand.

        Grain:
            date + store_id + product_id

        Missing store-product days are represented as
        zero demand.
        """

        # ---------------------------------------------------------
        # 1. Convert transaction timestamp to business date
        # ---------------------------------------------------------

        transactions = (
            df
            .withColumn(
                "date",
                F.to_date("transaction_timestamp"),
            )
        )

        # ---------------------------------------------------------
        # 2. Aggregate transaction-level data
        # ---------------------------------------------------------

        daily = (
            transactions
            .groupBy(
                "date",
                "store_id",
                "product_id",
            )
            .agg(
                F.first("product_name", ignorenulls=True)
                    .alias("product_name"),

                F.first("category", ignorenulls=True)
                    .alias("category"),

                F.first("subcategory", ignorenulls=True)
                    .alias("subcategory"),

                F.first("brand", ignorenulls=True)
                    .alias("brand"),

                F.first("supplier_id", ignorenulls=True)
                    .alias("supplier_id"),

                F.first("currency", ignorenulls=True)
                    .alias("currency"),

                F.sum("quantity")
                    .alias("quantity_sold"),

                F.sum("total_amount_cents")
                    .alias("revenue_cents"),

                F.count("*")
                    .alias("transactions"),

                F.avg("unit_price_cents")
                    .alias("average_unit_price_cents"),

                F.sum("discount_cents")
                    .alias("discount_cents"),

                F.sum("tax_cents")
                    .alias("tax_cents"),

                F.max("inventory_after")
                    .alias("inventory_end"),

                F.min("inventory_before")
                    .alias("inventory_min_before"),
            )
        )

        # ---------------------------------------------------------
        # 3. Calendar features
        # ---------------------------------------------------------

        daily = (
            daily
            .withColumn(
                "day_of_week",
                F.dayofweek("date"),
            )
            .withColumn(
                "day_of_month",
                F.dayofmonth("date"),
            )
            .withColumn(
                "month",
                F.month("date"),
            )
            .withColumn(
                "year",
                F.year("date"),
            )
        )

        return daily