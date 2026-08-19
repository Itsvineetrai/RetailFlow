from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder


class DemandForecaster:
    """Local scikit-learn demand forecasting engine."""

    FORECAST_DAYS = 7
    HISTORY_DAYS = 28

    MODEL_FEATURES = [
        "store_id",
        "product_id",
        "lag_1",
        "lag_7",
        "lag_14",
        "lag_28",
        "rolling_mean_7",
        "rolling_mean_14",
        "rolling_mean_28",
        "promotion_applied",
        "promotion_transactions",
        "inventory_min_before",
        "average_unit_price_cents",
        "day_of_week",
        "day_of_month",
        "month",
    ]

    CATEGORICAL_FEATURES = [
        "store_id",
        "product_id",
    ]

    NUMERICAL_FEATURES = [
        "lag_1",
        "lag_7",
        "lag_14",
        "lag_28",
        "rolling_mean_7",
        "rolling_mean_14",
        "rolling_mean_28",
        "promotion_applied",
        "promotion_transactions",
        "inventory_min_before",
        "average_unit_price_cents",
        "day_of_week",
        "day_of_month",
        "month",
    ]

    def __init__(self) -> None:

        self.preprocessor = ColumnTransformer(
            transformers=[
                (
                    "categorical",
                    OneHotEncoder(
                        handle_unknown="ignore"
                    ),
                    self.CATEGORICAL_FEATURES,
                ),
                (
                    "numerical",
                    "passthrough",
                    self.NUMERICAL_FEATURES,
                ),
            ]
        )

        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.8,
            random_state=42,
            loss="squared_error",
        )

        self._trained = False

    def _build_features(
        self,
        history: pd.DataFrame,
    ) -> pd.DataFrame:

        history = history.copy()

        history["date"] = pd.to_datetime(
            history["date"]
        )

        history = history.sort_values(
            [
                "store_id",
                "product_id",
                "date",
            ]
        )

        rows = []

        for (store_id, product_id), group in history.groupby(
            ["store_id", "product_id"],
            sort=False,
        ):
            group = group.sort_values("date")

            values = (
                group["quantity_sold"]
                .astype(float)
                .tolist()
            )

            if len(values) < self.HISTORY_DAYS:
                continue

            for index in range(
                self.HISTORY_DAYS,
                len(group),
            ):
                row = group.iloc[index]

                previous = values[:index]

                rows.append(
                    {
                        "store_id": store_id,
                        "product_id": product_id,
                        "lag_1": previous[-1],
                        "lag_7": previous[-7],
                        "lag_14": previous[-14],
                        "lag_28": previous[-28],
                        "rolling_mean_7": np.mean(
                            previous[-7:]
                        ),
                        "rolling_mean_14": np.mean(
                            previous[-14:]
                        ),
                        "rolling_mean_28": np.mean(
                            previous[-28:]
                        ),
                        "promotion_applied": float(
                            row["promotion_applied"]
                        ),
                        "promotion_transactions": float(
                            row["promotion_transactions"]
                        ),
                        "inventory_min_before": float(
                            row["inventory_min_before"]
                        ),
                        "average_unit_price_cents": float(
                            row["average_unit_price_cents"]
                        ),
                        "day_of_week": row["date"].dayofweek,
                        "day_of_month": row["date"].day,
                        "month": row["date"].month,
                        "target": float(
                            row["quantity_sold"]
                        ),
                    }
                )

        return pd.DataFrame(rows)

    def fit(
        self,
        history: pd.DataFrame,
    ) -> None:

        training_data = self._build_features(
            history
        )

        if training_data.empty:
            raise ValueError(
                "Unable to build forecasting training dataset."
            )

        X = training_data[
            self.MODEL_FEATURES
        ]

        y = training_data["target"]

        X_matrix = self.preprocessor.fit_transform(X)

        self.model.fit(
            X_matrix,
            y,
        )

        self._trained = True

    def forecast(
        self,
        history: pd.DataFrame,
    ) -> pd.DataFrame:

        if not self._trained:
            raise RuntimeError(
                "DemandForecaster must be fitted before forecasting."
            )

        history = history.copy()

        history["date"] = pd.to_datetime(
            history["date"]
        )

        history = history.sort_values(
            "date"
        )

        max_date = history["date"].max()

        pairs = (
            history[
                [
                    "store_id",
                    "product_id",
                ]
            ]
            .drop_duplicates()
            .sort_values(
                [
                    "store_id",
                    "product_id",
                ]
            )
            .reset_index(drop=True)
        )

        demand_history = {}

        for (
            store_id,
            product_id,
        ), group in history.groupby(
            [
                "store_id",
                "product_id",
            ],
            sort=False,
        ):

            values = (
                group.sort_values("date")[
                    "quantity_sold"
                ]
                .astype(float)
                .tail(self.HISTORY_DAYS)
                .tolist()
            )

            if len(values) != self.HISTORY_DAYS:
                raise ValueError(
                    f"{store_id}/{product_id} has "
                    f"{len(values)} history rows; "
                    f"expected {self.HISTORY_DAYS}."
                )

            demand_history[
                (store_id, product_id)
            ] = values

        latest_rows = (
            history
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

        latest_exogenous = {
            (
                row.store_id,
                row.product_id,
            ): {
                "promotion_applied": float(
                    row.promotion_applied
                ),
                "promotion_transactions": float(
                    row.promotion_transactions
                ),
                "inventory_min_before": float(
                    row.inventory_min_before
                ),
                "average_unit_price_cents": float(
                    row.average_unit_price_cents
                ),
            }
            for row in latest_rows.itertuples(
                index=False
            )
        }

        working_history = {
            key: list(values)
            for key, values in demand_history.items()
        }

        forecast_rows = []

        for day_offset in range(
            self.FORECAST_DAYS
        ):

            forecast_date = (
                max_date
                + timedelta(days=day_offset + 1)
            )

            day_rows = []

            for row in pairs.itertuples(
                index=False
            ):

                key = (
                    row.store_id,
                    row.product_id,
                )

                values = working_history[key]

                exog = latest_exogenous[key]

                row_features = {
                    "store_id": row.store_id,
                    "product_id": row.product_id,
                    "lag_1": values[-1],
                    "lag_7": values[-7],
                    "lag_14": values[-14],
                    "lag_28": values[-28],
                    "rolling_mean_7": float(
                        np.mean(values[-7:])
                    ),
                    "rolling_mean_14": float(
                        np.mean(values[-14:])
                    ),
                    "rolling_mean_28": float(
                        np.mean(values[-28:])
                    ),
                    "promotion_applied": exog[
                        "promotion_applied"
                    ],
                    "promotion_transactions": exog[
                        "promotion_transactions"
                    ],
                    "inventory_min_before": exog[
                        "inventory_min_before"
                    ],
                    "average_unit_price_cents": exog[
                        "average_unit_price_cents"
                    ],
                    "day_of_week": forecast_date.dayofweek,
                    "day_of_month": forecast_date.day,
                    "month": forecast_date.month,
                }

                day_rows.append(
                    row_features
                )

            day_features = pd.DataFrame(
                day_rows
            )

            day_matrix = (
                self.preprocessor.transform(
                    day_features[
                        self.MODEL_FEATURES
                    ]
                )
            )

            predictions = np.maximum(
                self.model.predict(
                    day_matrix
                ),
                0.0,
            )

            for feature_row, prediction in zip(
                day_rows,
                predictions,
            ):

                key = (
                    feature_row["store_id"],
                    feature_row["product_id"],
                )

                predicted_demand = float(
                    prediction
                )

                working_history[key].append(
                    predicted_demand
                )

                working_history[key] = (
                    working_history[key][
                        -self.HISTORY_DAYS:
                    ]
                )

                forecast_rows.append(
                    {
                        "date": forecast_date.date(),
                        "store_id": feature_row[
                            "store_id"
                        ],
                        "product_id": feature_row[
                            "product_id"
                        ],
                        "predicted_demand": predicted_demand,
                    }
                )

        return pd.DataFrame(
            forecast_rows
        )