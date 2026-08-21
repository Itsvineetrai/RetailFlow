"""Forecast lookup tools for the RetailFlow analytical agent."""

from __future__ import annotations

from datetime import date

from agent.gold_reader import load_gold


def get_demand_forecast(
    store_id: str | None = None,
    product_id: str | None = None,
) -> list[dict]:
    """Return the latest Gold demand forecast, optionally filtered."""
    df = load_gold("demand_forecast")

    if store_id is not None:
        df = df[df["store_id"].astype(str) == str(store_id)]

    if product_id is not None:
        df = df[df["product_id"].astype(str) == str(product_id)]

    if df.empty:
        return []

    df = df.sort_values(["date", "store_id", "product_id"])
    df["date"] = df["date"].astype(str)
    return df.to_dict(orient="records")


def get_forecast_summary(
    store_id: str | None = None,
    product_id: str | None = None,
) -> dict:
    """Return compact forecast facts suitable for an LLM context."""
    rows = get_demand_forecast(store_id=store_id, product_id=product_id)

    if not rows:
        return {"count": 0, "rows": []}

    return {
        "count": len(rows),
        "forecast_start": rows[0]["date"],
        "forecast_end": rows[-1]["date"],
        "total_predicted_demand": sum(
            float(row["predicted_demand"]) for row in rows
        ),
        "rows": rows,
    }
