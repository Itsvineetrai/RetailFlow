"""
RetailFlow Store Master Data

Master store catalog used throughout the RetailFlow platform.

This file represents a simplified store dimension.

Used by:
- POS Batch Generator
- Inventory Pipeline
- Supply Chain
- Forecasting
- Gold Analytics
"""

from __future__ import annotations

STORES = [
    {
        "store_id": "STR001",
        "store_name": "RetailFlow Connaught Place",
        "country": "India",
        "state": "Delhi",
        "city": "New Delhi",
        "region": "North",
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "store_type": "Flagship",
        "opened_year": 2018,
    },
    {
        "store_id": "STR002",
        "store_name": "RetailFlow Bandra",
        "country": "India",
        "state": "Maharashtra",
        "city": "Mumbai",
        "region": "West",
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "store_type": "Mall",
        "opened_year": 2019,
    },
    {
        "store_id": "STR003",
        "store_name": "RetailFlow Indiranagar",
        "country": "India",
        "state": "Karnataka",
        "city": "Bengaluru",
        "region": "South",
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "store_type": "Flagship",
        "opened_year": 2020,
    },
    {
        "store_id": "STR004",
        "store_name": "RetailFlow Salt Lake",
        "country": "India",
        "state": "West Bengal",
        "city": "Kolkata",
        "region": "East",
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "store_type": "High Street",
        "opened_year": 2021,
    },
    {
        "store_id": "STR005",
        "store_name": "RetailFlow T Nagar",
        "country": "India",
        "state": "Tamil Nadu",
        "city": "Chennai",
        "region": "South",
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "store_type": "Mall",
        "opened_year": 2022,
    },
]