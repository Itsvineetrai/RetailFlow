from __future__ import annotations

import pandas as pd
from core.constants import GOLD_FORECASTING_DATASET_PATH
from core.logger import get_logger
from core.spark_session import SparkSessionManager
from core.config import settings
from pipelines.gold.demand_forecaster import DemandForecaster
from pipelines.gold.demand_forecast_writer import (
    write_demand_forecast,
)


logger = get_logger(__name__)


# Gold Delta destination
GOLD_DEMAND_FORECAST_URI = (
    "s3://retailflow/gold/demand_forecast"
)


REQUIRED_COLUMNS = [
    "date",
    "store_id",
    "product_id",
    "quantity_sold",
    "promotion_applied",
    "promotion_transactions",
    "inventory_min_before",
    "average_unit_price_cents",
]


def load_history() -> pd.DataFrame:

    logger.info(
        "Loading Gold forecasting dataset..."
    )

    spark = SparkSessionManager.get_session(
        app_name="RetailFlow-Demand-Forecast"
    )

    spark.sparkContext.setLogLevel("ERROR")

    df = (
        spark.read
        .format("delta")
        .load(
            GOLD_FORECASTING_DATASET_PATH
        )
    )

    history_pdf = (
        df
        .select(*REQUIRED_COLUMNS)
        .toPandas()
    )

    spark.stop()

    logger.info(
        f"Historical rows loaded: {len(history_pdf):,}"
    )

    return history_pdf


def validate_forecast(
    history_pdf: pd.DataFrame,
    forecast_pdf: pd.DataFrame,
) -> None:

    expected_pairs = (
        history_pdf[
            ["store_id", "product_id"]
        ]
        .drop_duplicates()
        .shape[0]
    )

    actual_pairs = (
        forecast_pdf[
            ["store_id", "product_id"]
        ]
        .drop_duplicates()
        .shape[0]
    )

    forecast_dates = (
        forecast_pdf["date"]
        .nunique()
    )

    negative_predictions = (
        forecast_pdf["predicted_demand"] < 0
    ).sum()

    null_predictions = (
        forecast_pdf["predicted_demand"]
        .isna()
        .sum()
    )

    expected_start = (
        history_pdf["date"].max()
        + pd.Timedelta(days=1)
    ).date()

    expected_end = (
        history_pdf["date"].max()
        + pd.Timedelta(days=7)
    ).date()

    assert len(forecast_pdf) == (
        expected_pairs * 7
    )

    assert actual_pairs == expected_pairs

    assert forecast_dates == 7

    assert negative_predictions == 0

    assert null_predictions == 0

    assert (
        forecast_pdf["date"].min()
        == expected_start
    )

    assert (
        forecast_pdf["date"].max()
        == expected_end
    )

    logger.success(
        "Forecast validation passed: "
        f"{len(forecast_pdf)} rows, "
        f"{actual_pairs} pairs, "
        f"{forecast_dates} days."
    )


def main() -> None:

    logger.info(
        "Starting RetailFlow demand forecasting..."
    )

    # --------------------------------------------------
    # 1. Load historical Gold dataset
    # --------------------------------------------------

    history_pdf = load_history()

    history_pdf["date"] = pd.to_datetime(
        history_pdf["date"]
    )

    # --------------------------------------------------
    # 2. Train local ML model
    # --------------------------------------------------

    forecaster = DemandForecaster()

    forecaster.fit(
        history_pdf
    )

    logger.success(
        "Demand forecasting model trained."
    )

    # --------------------------------------------------
    # 3. Generate 7-day forecast
    # --------------------------------------------------

    forecast_pdf = forecaster.forecast(
        history_pdf
    )

    logger.info(
        f"Forecast generated: "
        f"{len(forecast_pdf)} rows."
    )

    # --------------------------------------------------
    # 4. Validate forecast
    # --------------------------------------------------

    validate_forecast(
        history_pdf,
        forecast_pdf,
    )

    # --------------------------------------------------
    # 5. Load MinIO credentials
    # --------------------------------------------------

    endpoint = settings.minio_endpoint

    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"http://{endpoint}"

    storage_options = {
        "AWS_ACCESS_KEY_ID": settings.minio_access_key,
        "AWS_SECRET_ACCESS_KEY": settings.minio_secret_key,
        "AWS_ENDPOINT_URL": endpoint,
        "AWS_REGION": "us-east-1",
        "AWS_ALLOW_HTTP": "true",
    }
    logger.info(
    f"Delta-RS endpoint: {storage_options['AWS_ENDPOINT_URL']}"
    )
    # --------------------------------------------------
    # 6. Persist forecast to Gold
    # --------------------------------------------------

    logger.info(
        "Writing demand forecast to Gold..."
    )

    write_demand_forecast(
        forecast_pdf=forecast_pdf,
        target_uri=GOLD_DEMAND_FORECAST_URI,
        storage_options=storage_options,
    )

    logger.success(
        "Demand forecast Gold write completed."
    )


if __name__ == "__main__":
    main()