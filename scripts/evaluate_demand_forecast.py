from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)

from core.constants import GOLD_FORECASTING_DATASET_PATH
from core.config import settings
from core.spark_session import SparkSessionManager
from pipelines.gold.demand_forecaster import DemandForecaster


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

HOLDOUT_DAYS = 7

REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "forecast_evaluation.json"
)


def load_history() -> pd.DataFrame:

    spark = SparkSessionManager.get_session(
        app_name="RetailFlow-Forecast-Evaluation"
    )

    spark.sparkContext.setLogLevel("ERROR")

    df = (
        spark.read
        .format("delta")
        .load(
            GOLD_FORECASTING_DATASET_PATH
        )
    )

    pdf = (
        df
        .select(*REQUIRED_COLUMNS)
        .toPandas()
    )

    spark.stop()

    pdf["date"] = pd.to_datetime(
        pdf["date"]
    )

    pdf["quantity_sold"] = pd.to_numeric(
        pdf["quantity_sold"],
        errors="raise",
    ).astype(float)

    for column in [
        "promotion_applied",
        "promotion_transactions",
        "inventory_min_before",
        "average_unit_price_cents",
    ]:
        pdf[column] = pd.to_numeric(
            pdf[column],
            errors="coerce",
        )

    return (
        pdf
        .sort_values(
            [
                "store_id",
                "product_id",
                "date",
            ]
        )
        .reset_index(drop=True)
    )


def calculate_metrics(
    actual: pd.Series,
    predicted: pd.Series,
) -> dict:

    actual_values = actual.to_numpy(
        dtype=float
    )

    predicted_values = predicted.to_numpy(
        dtype=float
    )

    mae = mean_absolute_error(
        actual_values,
        predicted_values,
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual_values,
            predicted_values,
        )
    )

    denominator = np.abs(
        actual_values
    ).sum()

    wape = (
        np.abs(
            actual_values
            - predicted_values
        ).sum()
        / denominator
        if denominator > 0
        else np.nan
    )

    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "WAPE": float(wape),
    }


def build_naive_forecast(
    train: pd.DataFrame,
    forecast_dates: pd.DatetimeIndex,
) -> pd.DataFrame:

    rows = []

    latest = (
        train
        .sort_values("date")
        .groupby(
            [
                "store_id",
                "product_id",
            ],
            as_index=False,
        )
        .tail(1)
    )

    for row in latest.itertuples(
        index=False
    ):

        for forecast_date in forecast_dates:

            rows.append(
                {
                    "date": forecast_date,
                    "store_id": row.store_id,
                    "product_id": row.product_id,
                    "predicted_demand": float(
                        row.quantity_sold
                    ),
                }
            )

    return pd.DataFrame(rows)


def build_lag7_forecast(
    train: pd.DataFrame,
    forecast_dates: pd.DatetimeIndex,
) -> pd.DataFrame:

    lookup = (
        train[
            [
                "date",
                "store_id",
                "product_id",
                "quantity_sold",
            ]
        ]
        .copy()
    )

    lookup["date"] = pd.to_datetime(
        lookup["date"]
    )

    rows = []

    pairs = (
        train[
            [
                "store_id",
                "product_id",
            ]
        ]
        .drop_duplicates()
    )

    for forecast_date in forecast_dates:

        lag_date = (
            forecast_date
            - pd.Timedelta(days=7)
        )

        matching = lookup[
            lookup["date"] == lag_date
        ][
            [
                "store_id",
                "product_id",
                "quantity_sold",
            ]
        ]

        frame = pairs.merge(
            matching,
            on=[
                "store_id",
                "product_id",
            ],
            how="left",
        )

        frame["date"] = forecast_date

        frame["predicted_demand"] = (
            frame["quantity_sold"]
            .fillna(0.0)
        )

        rows.append(
            frame[
                [
                    "date",
                    "store_id",
                    "product_id",
                    "predicted_demand",
                ]
            ]
        )

    return pd.concat(
        rows,
        ignore_index=True,
    )


def main() -> None:

    print(
        "Loading Gold forecasting dataset..."
    )

    history = load_history()

    max_date = history["date"].max()

    holdout_start = (
        max_date
        - pd.Timedelta(
            days=HOLDOUT_DAYS - 1
        )
    )

    train = history[
        history["date"] < holdout_start
    ].copy()

    actual = history[
        history["date"] >= holdout_start
    ].copy()

    forecast_dates = pd.date_range(
        holdout_start,
        max_date,
        freq="D",
    )

    print()
    print("=" * 70)
    print("TIME-BASED FORECAST EVALUATION")
    print("=" * 70)
    print(
        "Training range:",
        train["date"].min().date(),
        "->",
        train["date"].max().date(),
    )
    print(
        "Holdout range:",
        actual["date"].min().date(),
        "->",
        actual["date"].max().date(),
    )
    print(
        "Training rows:",
        len(train),
    )
    print(
        "Holdout rows:",
        len(actual),
    )
    print()

    # --------------------------------------------------
    # 1. Naive baseline
    # --------------------------------------------------

    naive = build_naive_forecast(
        train,
        forecast_dates,
    )

    # --------------------------------------------------
    # 2. Lag-7 baseline
    # --------------------------------------------------

    lag7 = build_lag7_forecast(
        train,
        forecast_dates,
    )

    # --------------------------------------------------
    # 3. Gradient Boosting
    # --------------------------------------------------

    model = DemandForecaster()

    model.fit(train)

    model_forecast = model.forecast(
        train
    )

    # --------------------------------------------------
    # Align actual observations
    # --------------------------------------------------

    actual_eval = actual[
        [
            "date",
            "store_id",
            "product_id",
            "quantity_sold",
        ]
    ].copy()
    actual_eval["date"] = pd.to_datetime(
    actual_eval["date"]
    ).dt.date

    actual_eval = actual_eval.rename(
        columns={
            "quantity_sold": "actual_demand"
        }
    )

    def evaluate(
        forecast: pd.DataFrame,
    ) -> dict:
        
        forecast=forecast.copy()
        forecast["date"] = pd.to_datetime(
            forecast["date"]
        ).dt.date

        merged = actual_eval.merge(
            forecast,
            on=[
                "date",
                "store_id",
                "product_id",
            ],
            how="inner",
        )

        if len(merged) != len(
            actual_eval
        ):
            raise ValueError(
                "Forecast/actual grain mismatch."
            )

        metrics = calculate_metrics(
            merged["actual_demand"],
            merged["predicted_demand"],
        )

        return metrics

    naive_metrics = evaluate(
        naive
    )

    lag7_metrics = evaluate(
        lag7
    )

    model_metrics = evaluate(
        model_forecast
    )

    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    results = pd.DataFrame(
        [
            {
                "model": "Naive",
                **naive_metrics,
            },
            {
                "model": "Lag-7",
                **lag7_metrics,
            },
            {
                "model": "Gradient Boosting",
                **model_metrics,
            },
        ]
    )

    print(
        results.to_string(
            index=False,
            formatters={
                "MAE": "{:.4f}".format,
                "RMSE": "{:.4f}".format,
                "WAPE": lambda x: (
                    f"{x * 100:.2f}%"
                ),
            },
        )
    )

    lag7_wape = (
        lag7_metrics["WAPE"]
    )

    model_wape = (
        model_metrics["WAPE"]
    )

    improvement = (
        (
            lag7_wape
            - model_wape
        )
        / lag7_wape
        * 100
        if lag7_wape > 0
        else np.nan
    )

    print()
    print(
        f"Gradient Boosting WAPE improvement "
        f"vs Lag-7: {improvement:.2f}%"
    )
    report = {
        "evaluation": {
            "training_start": train["date"].min().date().isoformat(),
            "training_end": train["date"].max().date().isoformat(),
            "holdout_start": actual["date"].min().date().isoformat(),
            "holdout_end": actual["date"].max().date().isoformat(),
            "training_rows": int(len(train)),
            "holdout_rows": int(len(actual)),
            "holdout_pairs": int(
                actual[
                    ["store_id", "product_id"]
                ]
                .drop_duplicates()
                .shape[0]
            ),
        },
        "models": {
            "naive": {
                "mae": round(
                    naive_metrics["MAE"],
                    4,
                ),
                "rmse": round(
                    naive_metrics["RMSE"],
                    4,
                ),
                "wape": round(
                    naive_metrics["WAPE"],
                    6,
                ),
            },
            "lag_7": {
                "mae": round(
                    lag7_metrics["MAE"],
                    4,
                ),
                "rmse": round(
                    lag7_metrics["RMSE"],
                    4,
                ),
                "wape": round(
                    lag7_metrics["WAPE"],
                    6,
                ),
            },
            "gradient_boosting": {
                "mae": round(
                    model_metrics["MAE"],
                    4,
                ),
                "rmse": round(
                    model_metrics["RMSE"],
                    4,
                ),
                "wape": round(
                    model_metrics["WAPE"],
                    6,
                ),
            },
        },
        "improvement": {
            "metric": "WAPE",
            "baseline": "lag_7",
            "value_percent": round(
                float(improvement),
                2,
            ),
        },
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Evaluation report written to: "
        f"{REPORT_PATH}"
    )
    
    print(
        "Forecast accuracy evaluation: PASSED"
    )


if __name__ == "__main__":
    main()