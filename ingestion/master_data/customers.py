"""
RetailFlow Customer Master Data

Master customer catalog used across the RetailFlow platform.

Used by:
- POS Batch Generator
- Customer Analytics
- Loyalty Programs
- Demand Forecasting
- Gold Layer Analytics

NOTE:
No personally identifiable information (PII) is stored.
"""

from __future__ import annotations

CUSTOMERS = [
    {
        "customer_id": "CUST000001",
        "customer_segment": "Regular",
        "loyalty_member": True,
        "country": "India",
        "city": "New Delhi",
        "preferred_payment": "UPI",
    },
    {
        "customer_id": "CUST000002",
        "customer_segment": "Premium",
        "loyalty_member": True,
        "country": "India",
        "city": "Mumbai",
        "preferred_payment": "Credit Card",
    },
    {
        "customer_id": "CUST000003",
        "customer_segment": "Regular",
        "loyalty_member": False,
        "country": "India",
        "city": "Bengaluru",
        "preferred_payment": "Debit Card",
    },
    {
        "customer_id": "CUST000004",
        "customer_segment": "Corporate",
        "loyalty_member": True,
        "country": "India",
        "city": "Hyderabad",
        "preferred_payment": "Bank Transfer",
    },
    {
        "customer_id": "CUST000005",
        "customer_segment": "Regular",
        "loyalty_member": False,
        "country": "India",
        "city": "Chennai",
        "preferred_payment": "Cash",
    },
    {
        "customer_id": "CUST000006",
        "customer_segment": "Premium",
        "loyalty_member": True,
        "country": "India",
        "city": "Kolkata",
        "preferred_payment": "UPI",
    },
    {
        "customer_id": "CUST000007",
        "customer_segment": "Regular",
        "loyalty_member": True,
        "country": "India",
        "city": "Pune",
        "preferred_payment": "Credit Card",
    },
    {
        "customer_id": "CUST000008",
        "customer_segment": "Corporate",
        "loyalty_member": False,
        "country": "India",
        "city": "Ahmedabad",
        "preferred_payment": "Bank Transfer",
    },
    {
        "customer_id": "CUST000009",
        "customer_segment": "Premium",
        "loyalty_member": True,
        "country": "India",
        "city": "Jaipur",
        "preferred_payment": "Wallet",
    },
    {
        "customer_id": "CUST000010",
        "customer_segment": "Regular",
        "loyalty_member": False,
        "country": "India",
        "city": "Lucknow",
        "preferred_payment": "UPI",
    },
]