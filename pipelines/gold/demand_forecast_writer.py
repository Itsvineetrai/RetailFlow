from __future__ import annotations

import pandas as pd
from deltalake import write_deltalake


def write_demand_forecast(
    forecast_pdf: pd.DataFrame,
    target_uri: str,
    storage_options: dict,
) -> None:
    """
    Persist the validated demand forecast to Gold Delta
    using Delta-RS.
    """

    required_columns = [
        "date",
        "store_id",
        "product_id",
        "predicted_demand",
    ]

    missing = [
        column
        for column in required_columns
        if column not in forecast_pdf.columns
    ]

    if missing:
        raise ValueError(
            f"Missing forecast columns: {missing}"
        )

    output = forecast_pdf[
        required_columns
    ].copy()

    output["date"] = pd.to_datetime(
        output["date"]
    ).dt.date

    output["predicted_demand"] = pd.to_numeric(
        output["predicted_demand"],
        errors="raise",
    )

    if output.empty:
        raise ValueError(
            "Cannot write an empty demand forecast."
        )

    if output["predicted_demand"].isna().any():
        raise ValueError(
            "Forecast contains null predictions."
        )

    if (
        output["predicted_demand"] < 0
    ).any():
        raise ValueError(
            "Forecast contains negative predictions."
        )

    write_deltalake(
        target_uri,
        output,
        mode="overwrite",
        storage_options=storage_options,
    )