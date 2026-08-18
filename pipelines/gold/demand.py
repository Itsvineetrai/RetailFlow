"""
RetailFlow Gold Demand Metrics.

Creates the canonical daily demand dataset used by
forecasting and inventory analytics.

Grain
-----
One row per:

    date + store_id + product_id

The dataset is intentionally separate from reporting-oriented
sales metrics because forecasting requires a stable time-series
grain.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from core.logger import get_logger


logger = get_logger(__name__)


class DemandMetrics:
    """
    Build forecasting-ready daily demand metrics.
    """

    @staticmethod
    def daily_demand(df: DataFrame) -> DataFrame:
        """
        Aggregate transaction-level Silver data into daily
        store-product demand observations.

        Expected input columns include:

            transaction_timestamp
            store_id
            product_id
            product_name
            category
            subcategory
            brand
            supplier_id
            quantity
            unit_price_cents
            discount_cents
            tax_cents
            total_amount_cents
            currency
            promotion_id
            inventory_before
            inventory_after

        Returns
        -------
        DataFrame
            One row per date/store/product combination.
        """

        logger.info(
            "Building canonical daily demand dataset..."
        )

        required_columns = {
            "transaction_timestamp",
            "store_id",
            "product_id",
            "product_name",
            "category",
            "subcategory",
            "brand",
            "supplier_id",
            "quantity",
            "unit_price_cents",
            "discount_cents",
            "tax_cents",
            "total_amount_cents",
            "currency",
            "promotion_id",
            "inventory_before",
            "inventory_after",
        }

        missing_columns = sorted(
            required_columns.difference(df.columns)
        )

        if missing_columns:
            raise ValueError(
                "Silver transaction dataset is missing required "
                f"columns: {missing_columns}"
            )

        # ---------------------------------------------------------
        # 1. Parse transaction timestamp
        # ---------------------------------------------------------

        prepared_df = (
            df
            .withColumn(
                "_transaction_ts",
                F.to_timestamp(
                    F.col("transaction_timestamp")
                ),
            )
            .withColumn(
                "date",
                F.to_date(
                    F.col("_transaction_ts")
                ),
            )
        )

        # ---------------------------------------------------------
        # 2. Identify the final inventory state of each
        #    store-product pair for every day.
        #
        #    We use the latest transaction of the day.
        # ---------------------------------------------------------

        inventory_window = (
            Window
            .partitionBy(
                "date",
                "store_id",
                "product_id",
            )
            .orderBy(
                F.col("_transaction_ts").desc(),
            )
        )

        inventory_df = (
            prepared_df
            .withColumn(
                "_row_number",
                F.row_number().over(
                    inventory_window
                ),
            )
            .filter(
                F.col("_row_number") == 1
            )
            .select(
                "date",
                "store_id",
                "product_id",
                F.col(
                    "inventory_after"
                ).cast("long").alias(
                    "inventory_end"
                ),
            )
        )

        # ---------------------------------------------------------
        # 3. Aggregate transactional demand
        # ---------------------------------------------------------

        demand_df = (
            prepared_df
            .groupBy(
                "date",
                "store_id",
                "product_id",
                "product_name",
                "category",
                "subcategory",
                "brand",
                "supplier_id",
                "currency",
            )
            .agg(
                F.sum(
                    F.col("quantity")
                )
                .cast("long")
                .alias("quantity_sold"),

                F.sum(
                    F.col("total_amount_cents")
                )
                .cast("long")
                .alias("revenue_cents"),

                F.count("*")
                .cast("long")
                .alias("transactions"),

                F.avg(
                    F.col("unit_price_cents")
                    .cast("decimal(20,2)")
                )
                .cast("decimal(20,2)")
                .alias("average_unit_price_cents"),

                F.sum(
                    F.col("discount_cents")
                )
                .cast("long")
                .alias("discount_cents"),

                F.sum(
                    F.col("tax_cents")
                )
                .cast("long")
                .alias("tax_cents"),

                F.sum(
                    F.when(
                        F.col("promotion_id") != "PROMO000",
                        1,
                    ).otherwise(0)
                )
                .cast("long")
                .alias("promotion_transactions"),

                F.max(
                    F.when(
                        F.col("promotion_id") != "PROMO000",
                        1,
                    ).otherwise(0)
                )
                .cast("integer")
                .alias("promotion_applied"),

                F.min(
                    F.col("inventory_before")
                )
                .cast("long")
                .alias("inventory_min_before"),
            )
        )

        # ---------------------------------------------------------
        # 4. Add ending inventory
        # ---------------------------------------------------------

        result_df = (
            demand_df
            .join(
                inventory_df,
                on=[
                    "date",
                    "store_id",
                    "product_id",
                ],
                how="left",
            )
            .withColumn(
                "day_of_week",
                F.dayofweek(
                    F.col("date")
                ),
            )
            .withColumn(
                "day_of_month",
                F.dayofmonth(
                    F.col("date")
                ),
            )
            .withColumn(
                "month",
                F.month(
                    F.col("date")
                ),
            )
            .withColumn(
                "year",
                F.year(
                    F.col("date")
                ),
            )
        )

        # ---------------------------------------------------------
        # 5. Select stable column order
        # ---------------------------------------------------------

        result_df = result_df.select(
            "date",
            "store_id",
            "product_id",
            "product_name",
            "category",
            "subcategory",
            "brand",
            "supplier_id",
            "currency",
            "quantity_sold",
            "revenue_cents",
            "transactions",
            "average_unit_price_cents",
            "discount_cents",
            "tax_cents",
            "promotion_applied",
            "promotion_transactions",
            "inventory_min_before",
            "inventory_end",
            "day_of_week",
            "day_of_month",
            "month",
            "year",
        )

        logger.success(
            "Canonical daily demand dataset created."
        )

        return result_df