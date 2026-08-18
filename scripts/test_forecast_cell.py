"""Minimal reproducer for the notebook recursive-forecast cell."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

from pyspark.ml import Pipeline
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.ml.regression import GBTRegressor
from pyspark.sql import Row, functions as F
from pyspark.sql.types import (
    DateType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)
from pyspark.sql.window import Window

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.constants import GOLD_FORECASTING_DATASET_PATH
from core.spark_session import SparkSessionManager

EXPECTED_PAIRS = 50
EXPECTED_DAYS = 180
TEST_DAYS = 14
FORECAST_DAYS = 7
FORECAST_START = date(2026, 8, 13)

MODEL_FEATURES = [
    "lag_1", "lag_7", "lag_14", "lag_28",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
]

FEATURE_COLUMNS = [
    "store_id_encoded", "product_id_encoded",
    *MODEL_FEATURES,
    "promotion_applied", "promotion_transactions",
    "inventory_min_before", "average_unit_price_cents",
    "day_of_week", "day_of_month", "month",
]

FUTURE_ROW_SCHEMA = StructType([
    StructField("date", DateType(), False),
    StructField("store_id", StringType(), False),
    StructField("product_id", StringType(), False),
    StructField("lag_1", DoubleType(), False),
    StructField("lag_7", DoubleType(), False),
    StructField("lag_14", DoubleType(), False),
    StructField("lag_28", DoubleType(), False),
    StructField("rolling_mean_7", DoubleType(), False),
    StructField("rolling_mean_14", DoubleType(), False),
    StructField("rolling_mean_28", DoubleType(), False),
    StructField("promotion_applied", IntegerType(), False),
    StructField("promotion_transactions", IntegerType(), False),
    StructField("inventory_min_before", IntegerType(), False),
    StructField("average_unit_price_cents", DoubleType(), False),
    StructField("day_of_week", IntegerType(), False),
    StructField("day_of_month", IntegerType(), False),
    StructField("month", IntegerType(), False),
])


def spark_day_of_week(d: date) -> int:
    return (d.isoweekday() % 7) + 1


def main() -> None:
    spark = SparkSessionManager.get_session("Forecast-Repro")
    spark.sparkContext.setLogLevel("ERROR")

    forecasting_df = spark.read.format("delta").load(GOLD_FORECASTING_DATASET_PATH)
    time_window = Window.partitionBy("store_id", "product_id").orderBy("date")

    features_df = (
        forecasting_df
        .withColumn("lag_1", F.lag("quantity_sold", 1).over(time_window))
        .withColumn("lag_7", F.lag("quantity_sold", 7).over(time_window))
        .withColumn("lag_14", F.lag("quantity_sold", 14).over(time_window))
        .withColumn("lag_28", F.lag("quantity_sold", 28).over(time_window))
        .withColumn("rolling_mean_7", F.avg("quantity_sold").over(time_window.rowsBetween(-7, -1)))
        .withColumn("rolling_mean_14", F.avg("quantity_sold").over(time_window.rowsBetween(-14, -1)))
        .withColumn("rolling_mean_28", F.avg("quantity_sold").over(time_window.rowsBetween(-28, -1)))
    )
    model_df = features_df.dropna(subset=MODEL_FEATURES)

    last_model_date = model_df.agg(F.max("date")).collect()[0][0]
    test_start = last_model_date - timedelta(days=TEST_DAYS - 1)
    train_df = model_df.filter(F.col("date") < F.lit(test_start))
    test_df = model_df.filter(F.col("date") >= F.lit(test_start))

    encoder_pipeline = Pipeline(stages=[
        StringIndexer(inputCol="store_id", outputCol="store_id_index", handleInvalid="keep"),
        StringIndexer(inputCol="product_id", outputCol="product_id_index", handleInvalid="keep"),
        OneHotEncoder(inputCols=["store_id_index", "product_id_index"],
                        outputCols=["store_id_encoded", "product_id_encoded"]),
    ])
    encoder_model = encoder_pipeline.fit(train_df)
    assembler = VectorAssembler(inputCols=FEATURE_COLUMNS, outputCol="features", handleInvalid="skip")

    train_features = assembler.transform(encoder_model.transform(train_df))
    gbt = GBTRegressor(featuresCol="features", labelCol="quantity_sold", maxIter=10, maxDepth=3, seed=42)
    model = gbt.fit(train_features)
    print("Model trained.")

    history_window = Window.partitionBy("store_id", "product_id").orderBy(F.col("date").desc())
    history_rows = (
        forecasting_df.select(
            "date", "store_id", "product_id", "quantity_sold",
            "promotion_applied", "promotion_transactions",
            "inventory_min_before", "average_unit_price_cents",
        )
        .withColumn("_rn", F.row_number().over(history_window))
        .filter(F.col("_rn") <= 28)
        .drop("_rn")
        .orderBy("store_id", "product_id", "date")
        .collect()
    )

    demand_history: dict[tuple[str, str], list[float]] = {}
    latest_attributes: dict[tuple[str, str], Row] = {}
    for row in history_rows:
        key = (row["store_id"], row["product_id"])
        demand_history.setdefault(key, []).append(float(row["quantity_sold"]))
        latest_attributes[key] = row

    forecast_date = FORECAST_START
    future_rows = []
    for key, values in sorted(demand_history.items()):
        store_id, product_id = key
        attrs = latest_attributes[key]
        future_rows.append(Row(
            date=forecast_date,
            store_id=store_id,
            product_id=product_id,
            lag_1=values[-1],
            lag_7=values[-7],
            lag_14=values[-14],
            lag_28=values[-28],
            rolling_mean_7=sum(values[-7:]) / 7.0,
            rolling_mean_14=sum(values[-14:]) / 14.0,
            rolling_mean_28=sum(values[-28:]) / 28.0,
            promotion_applied=int(attrs["promotion_applied"] or 0),
            promotion_transactions=int(attrs["promotion_transactions"] or 0),
            inventory_min_before=int(attrs["inventory_min_before"] or 0),
            average_unit_price_cents=float(attrs["average_unit_price_cents"] or 0),
            day_of_week=spark_day_of_week(forecast_date),
            day_of_month=forecast_date.day,
            month=forecast_date.month,
        ))

    future_day_df = spark.createDataFrame(future_rows, schema=FUTURE_ROW_SCHEMA)
    print("Future DF schema:")
    future_day_df.printSchema()
    print("Sample row:", future_day_df.first())

    encoded = encoder_model.transform(future_day_df)
    print("Encoded columns:", encoded.columns)
    future_features = assembler.transform(encoded)
    print("Feature vector sample:", future_features.select("features").first())

    preds = model.transform(future_features).select("date", "store_id", "product_id", "prediction")
    print("Prediction count:", preds.count())
    preds.show(5)
    print("SUCCESS")


if __name__ == "__main__":
    main()
