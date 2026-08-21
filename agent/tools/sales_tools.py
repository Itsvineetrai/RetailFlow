"""Sales and financial lookup tools for the RetailFlow agent."""

from __future__ import annotations

from agent.gold_reader import load_gold


SALES_DATASETS = {
    "daily_sales",
    "store_sales",
    "category_sales",
    "city_sales",
    "top_products",
    "financial_summary",
    "payment_summary",
    "payment_finance",
}


def get_sales_dataset(dataset: str) -> list[dict]:
    """Return a current Gold sales/reporting dataset."""
    if dataset not in SALES_DATASETS:
        raise ValueError(f"Unsupported sales dataset: {dataset}")

    df = load_gold(dataset)
    if df.empty:
        return []

    return df.to_dict(orient="records")
