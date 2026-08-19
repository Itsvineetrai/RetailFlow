from functools import lru_cache

from deltalake import DeltaTable


GOLD_BASE_URI = "s3://retailflow/gold"


def _gold_uri(dataset: str) -> str:
    return f"{GOLD_BASE_URI}/{dataset}"


@lru_cache(maxsize=32)
def load_gold(dataset: str, storage_options_key: tuple) :
    storage_options = dict(storage_options_key)

    table = DeltaTable(
        _gold_uri(dataset),
        storage_options=storage_options,
    )

    return table.to_pandas()


def load_dataset(dataset: str, storage_options: dict):
    storage_options_key = tuple(
        sorted(storage_options.items())
    )

    return load_gold(
        dataset,
        storage_options_key,
    ).copy()


def load_all_gold(storage_options: dict) -> dict:
    datasets = [
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

    return {
        dataset: load_dataset(
            dataset,
            storage_options,
        )
        for dataset in datasets
    }