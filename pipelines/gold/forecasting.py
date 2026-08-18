from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


class ForecastingDatasetBuilder:

    @staticmethod
    def complete_grid(
        daily_df: DataFrame,
    ) -> DataFrame:
        """
        Build a complete date × store × product forecasting dataset.

        Grain:
            date + store_id + product_id

        Missing demand observations are represented as zero demand.

        Product attributes come from the product metadata already present
        in the daily demand dataset.
        """

        # ---------------------------------------------------------
        # 1. Build the three dimensions
        # ---------------------------------------------------------

        dates = (
            daily_df
            .select("date")
            .distinct()
        )

        stores = (
            daily_df
            .select("store_id")
            .distinct()
        )

        products = (
            daily_df
            .select(
                "product_id",
                "product_name",
                "category",
                "subcategory",
                "brand",
                "supplier_id",
                "currency",
            )
            .dropDuplicates(["product_id"])
        )

        # ---------------------------------------------------------
        # 2. Complete date × store × product grid
        #
        # Product attributes are intentionally kept here.
        # The later daily-data join contains metrics only, preventing
        # duplicate metadata columns.
        # ---------------------------------------------------------

        grid = (
            dates
            .crossJoin(stores)
            .crossJoin(products)
        )

        # ---------------------------------------------------------
        # 3. Keep only transactional metrics from daily demand
        #
        # Metadata already exists in the grid.
        # ---------------------------------------------------------

        daily_metrics = (
            daily_df
            .select(
                "date",
                "store_id",
                "product_id",
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
            )
        )

        # ---------------------------------------------------------
        # 4. Attach observed demand to complete grid
        # ---------------------------------------------------------

        result = (
            grid
            .join(
                daily_metrics,
                on=[
                    "date",
                    "store_id",
                    "product_id",
                ],
                how="left",
            )
        )

        # ---------------------------------------------------------
        # 5. Missing demand = zero
        # ---------------------------------------------------------

        result = (
            result
            .withColumn(
                "quantity_sold",
                F.coalesce(
                    F.col("quantity_sold"),
                    F.lit(0),
                ).cast("long"),
            )
            .withColumn(
                "revenue_cents",
                F.coalesce(
                    F.col("revenue_cents"),
                    F.lit(0),
                ).cast("long"),
            )
            .withColumn(
                "transactions",
                F.coalesce(
                    F.col("transactions"),
                    F.lit(0),
                ).cast("long"),
            )
            .withColumn(
                "discount_cents",
                F.coalesce(
                    F.col("discount_cents"),
                    F.lit(0),
                ).cast("long"),
            )
            .withColumn(
                "tax_cents",
                F.coalesce(
                    F.col("tax_cents"),
                    F.lit(0),
                ).cast("long"),
            )
            .withColumn(
                "promotion_applied",
                F.coalesce(
                    F.col("promotion_applied"),
                    F.lit(0),
                ).cast("integer"),
            )
            .withColumn(
                "promotion_transactions",
                F.coalesce(
                    F.col("promotion_transactions"),
                    F.lit(0),
                ).cast("long"),
            )
        )

        # ---------------------------------------------------------
        # 6. Calendar features
        # ---------------------------------------------------------

        result = (
            result
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

        # ---------------------------------------------------------
        # 7. Stable column order
        # ---------------------------------------------------------

        return result.select(
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