"""Inventory lookup tools for the RetailFlow analytical agent."""

from __future__ import annotations

from agent.gold_reader import load_gold


INVENTORY_DATASETS = {"inventory_current", "inventory_risk"}


def get_inventory_dataset(dataset: str) -> list[dict]:
    """Return a current Gold inventory dataset."""
    if dataset not in INVENTORY_DATASETS:
        raise ValueError(f"Unsupported inventory dataset: {dataset}")

    df = load_gold(dataset)
    if df.empty:
        return []

    return df.to_dict(orient="records")
