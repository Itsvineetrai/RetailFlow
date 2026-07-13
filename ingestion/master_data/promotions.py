"""
RetailFlow Promotion Master Data

Master promotion catalog used across the RetailFlow platform.

Used by:
- POS Batch Generator
- E-commerce Generator
- Financial Reporting
- Campaign Analytics
"""

from __future__ import annotations

PROMOTIONS = [
    {
        "promotion_id": "PROMO000",
        "promotion_name": "No Promotion",
        "promotion_type": "NONE",
        "discount_percentage": 0,
        "minimum_purchase_cents": 0,
        "active": True,
    },
    {
        "promotion_id": "PROMO001",
        "promotion_name": "Weekend Sale",
        "promotion_type": "PERCENTAGE",
        "discount_percentage": 10,
        "minimum_purchase_cents": 50000,
        "active": True,
    },
    {
        "promotion_id": "PROMO002",
        "promotion_name": "Festival Offer",
        "promotion_type": "PERCENTAGE",
        "discount_percentage": 20,
        "minimum_purchase_cents": 100000,
        "active": True,
    },
    {
        "promotion_id": "PROMO003",
        "promotion_name": "Clearance Sale",
        "promotion_type": "PERCENTAGE",
        "discount_percentage": 40,
        "minimum_purchase_cents": 0,
        "active": True,
    },
    {
        "promotion_id": "PROMO004",
        "promotion_name": "Buy More Save More",
        "promotion_type": "PERCENTAGE",
        "discount_percentage": 15,
        "minimum_purchase_cents": 250000,
        "active": True,
    },
    {
        "promotion_id": "PROMO005",
        "promotion_name": "Flash Sale",
        "promotion_type": "PERCENTAGE",
        "discount_percentage": 25,
        "minimum_purchase_cents": 150000,
        "active": False,
    },
]