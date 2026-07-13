"""
RetailFlow Supplier Master Data

Master supplier catalog used across the RetailFlow platform.

Used by:
- POS Batch Generator
- Supply Chain API
- Inventory Pipeline
- Purchase Orders
- Demand Forecasting
"""

from __future__ import annotations

SUPPLIERS = [
    {
        "supplier_id": "SUP001",
        "supplier_name": "Amul Dairy Ltd.",
        "country": "India",
        "city": "Anand",
        "currency": "INR",
        "lead_time_days": 2,
        "contact_email": "orders@amul.example",
        "rating": 4.8,
    },
    {
        "supplier_id": "SUP002",
        "supplier_name": "Fortune Foods",
        "country": "India",
        "city": "Ahmedabad",
        "currency": "INR",
        "lead_time_days": 5,
        "contact_email": "orders@fortune.example",
        "rating": 4.6,
    },
    {
        "supplier_id": "SUP003",
        "supplier_name": "Global Electronics Pvt Ltd",
        "country": "India",
        "city": "Bengaluru",
        "currency": "INR",
        "lead_time_days": 10,
        "contact_email": "orders@globalelectronics.example",
        "rating": 4.7,
    },
    {
        "supplier_id": "SUP004",
        "supplier_name": "Sports World Distributors",
        "country": "India",
        "city": "Mumbai",
        "currency": "INR",
        "lead_time_days": 7,
        "contact_email": "orders@sportsworld.example",
        "rating": 4.5,
    },
    {
        "supplier_id": "SUP005",
        "supplier_name": "Premium Electronics India",
        "country": "India",
        "city": "Noida",
        "currency": "INR",
        "lead_time_days": 8,
        "contact_email": "orders@premiumelectronics.example",
        "rating": 4.9,
    },
]