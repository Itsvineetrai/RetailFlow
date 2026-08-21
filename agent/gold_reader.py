"""Fresh, shared access to RetailFlow Gold Delta datasets."""

from __future__ import annotations

from deltalake import DeltaTable

from dashboard.config import get_storage_options


GOLD_BASE_URI = "s3://retailflow/gold"


def _gold_uri(dataset: str) -> str:
    """Return the canonical Gold Delta URI for a dataset."""
    if not dataset or dataset.strip() != dataset:
        raise ValueError("dataset must be a non-empty name without surrounding whitespace")
    if "/" in dataset or "\\" in dataset or ".." in dataset:
        raise ValueError("dataset must be a simple Gold dataset name")
    return f"{GOLD_BASE_URI}/{dataset}"


def load_gold(dataset: str):
    """Read the current version of a Gold Delta dataset into pandas.

    Deliberately does not cache the table. The dashboard agent should see
    the latest committed Gold version after an ingestion/forecast run.
    """
    table = DeltaTable(
        _gold_uri(dataset),
        storage_options=get_storage_options(),
    )
    return table.to_pandas()


def list_gold_datasets() -> list[str]:
    """Return datasets currently supported by the dashboard/agent."""
    return [
        "financial_summary",
        "daily_sales",
        "store_sales",
        "category_sales",
        "city_sales",
        "top_products",
        "payment_summary",
        "payment_finance",
        "loyalty_analysis",
        "customer_segments",
        "inventory_current",
        "inventory_risk",
        "demand_forecast",
    ]
