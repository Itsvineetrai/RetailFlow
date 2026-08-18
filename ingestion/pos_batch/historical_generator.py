from __future__ import annotations

import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from core.logger import get_logger
from core.minio_client import MinIOClient
from core.utils import ensure_directory

from ingestion.master_data.customers import CUSTOMERS
from ingestion.master_data.payment_methods import PAYMENT_METHODS
from ingestion.master_data.products import PRODUCTS
from ingestion.master_data.promotions import PROMOTIONS
from ingestion.master_data.stores import STORES


logger = get_logger(__name__)


class HistoricalPOSGenerator:
    """
    Generate synthetic historical POS transactions for forecasting experiments.

    The generator creates transaction-level records with:
        - daily/weekly demand patterns
        - store-level demand differences
        - product-level demand differences
        - promotion effects
        - persistent inventory state
        - realistic transaction timestamps

    This generator is intended for historical data simulation.
    The existing POSBatchGenerator remains responsible for normal
    current-time batch generation.
    """

    # Relative demand by store type.
    STORE_DEMAND_FACTORS = {
        "Flagship": 1.25,
        "Mall": 1.10,
        "High Street": 0.95,
    }

    # Relative demand by broad product category.
    CATEGORY_DEMAND_FACTORS = {
        "Groceries": 1.30,
        "Sports": 0.85,
        "Fashion": 0.90,
        "Electronics": 0.65,
    }

    # Weekly demand pattern.
    #
    # Monday = 0 ... Sunday = 6
    WEEKDAY_FACTORS = {
        0: 0.92,  # Monday
        1: 0.95,  # Tuesday
        2: 1.00,  # Wednesday
        3: 1.05,  # Thursday
        4: 1.15,  # Friday
        5: 1.30,  # Saturday
        6: 1.18,  # Sunday
    }

    def __init__(self, seed: int = 42) -> None:
        self.random = random.Random(seed)

        # Persistent inventory state:
        # (store_id, product_id) -> current inventory
        self.inventory: dict[tuple[str, str], int] = {}

        self._initialize_inventory()

    # ------------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------------

    def _initialize_inventory(self) -> None:
        """
        Initialize inventory independently for every store-product pair.
        """

        for store in STORES:
            for product in PRODUCTS:
                reorder_level = product["reorder_level"]

                # Start comfortably above reorder level.
                minimum = max(reorder_level * 3, 50)
                maximum = max(reorder_level * 8, minimum + 50)

                self.inventory[
                    (store["store_id"], product["product_id"])
                ] = self.random.randint(minimum, maximum)

    # ------------------------------------------------------------------
    # Demand
    # ------------------------------------------------------------------

    def _product_demand_factor(self, product: dict) -> float:
        """
        Estimate baseline product popularity.

        This intentionally uses only fields already present in
        PRODUCTS rather than adding artificial master-data fields.
        """

        category_factor = self.CATEGORY_DEMAND_FACTORS.get(
            product["category"],
            1.0,
        )

        # Cheaper everyday products tend to have higher unit demand.
        price = product["unit_price_cents"]

        if price <= 10_000:
            price_factor = 1.35
        elif price <= 100_000:
            price_factor = 1.10
        elif price <= 1_000_000:
            price_factor = 0.85
        else:
            price_factor = 0.55

        return category_factor * price_factor

    def _store_demand_factor(self, store: dict) -> float:
        return self.STORE_DEMAND_FACTORS.get(
            store["store_type"],
            1.0,
        )

    def _promotion(self, date: datetime) -> dict:
        """
        Select a promotion appropriate for the simulated date.

        Flash Sale is excluded because the master data marks it inactive.
        """

        active_promotions = [
            promotion
            for promotion in PROMOTIONS
            if promotion.get("active", False)
            and promotion["promotion_type"] != "NONE"
        ]

        # Weekend promotions receive higher probability on weekends.
        if date.weekday() >= 5:
            weekend_promotions = [
                promotion
                for promotion in active_promotions
                if promotion["promotion_id"] == "PROMO001"
            ]

            if weekend_promotions and self.random.random() < 0.45:
                return weekend_promotions[0]

        # Most transactions should have no promotion.
        if self.random.random() < 0.65:
            return next(
                promotion
                for promotion in PROMOTIONS
                if promotion["promotion_type"] == "NONE"
            )

        return self.random.choice(active_promotions)

    def _expected_quantity(
        self,
        store: dict,
        product: dict,
        date: datetime,
        promotion: dict,
    ) -> int:
        """
        Generate expected demand for a store-product-day combination.
        """

        product_factor = self._product_demand_factor(product)
        store_factor = self._store_demand_factor(store)
        weekday_factor = self.WEEKDAY_FACTORS[date.weekday()]

        promotion_factor = 1.0

        if promotion["promotion_id"] != "PROMO000":
            promotion_factor += (
                promotion["discount_percentage"] / 100
            ) * 1.5

        # Base demand differs by category.
        if product["category"] == "Groceries":
            base_demand = 7
        elif product["category"] == "Sports":
            base_demand = 4
        elif product["category"] == "Fashion":
            base_demand = 4
        else:
            base_demand = 2

        expected = (
            base_demand
            * product_factor
            * store_factor
            * weekday_factor
            * promotion_factor
        )

        # Small deterministic seasonal wave across the 60-day period.
        seasonal_factor = 1.0 + (
            0.08 * math.sin(date.timetuple().tm_yday / 8)
        )

        expected *= seasonal_factor

        # Gaussian noise gives the model something realistic to learn.
        noise = self.random.gauss(1.0, 0.20)

        quantity = max(
            1,
            round(expected * max(0.3, noise)),
        )

        return quantity

    # ------------------------------------------------------------------
    # Transaction
    # ------------------------------------------------------------------

    def _transaction(
        self,
        store: dict,
        product: dict,
        customer: dict,
        payment: dict,
        promotion: dict,
        timestamp: datetime,
        quantity: int,
    ) -> dict:
        key = (
            store["store_id"],
            product["product_id"],
        )

        before = self.inventory[key]

        # Never sell more than available inventory.
        quantity = min(quantity, before)

        # If inventory is exhausted, replenish from a simulated
        # supplier restock event. This keeps the historical dataset
        # useful for demand forecasting without creating impossible
        # negative inventory.
        if quantity <= 0:
            replenishment = max(
                product["reorder_level"] * 3,
                50,
            )

            before += replenishment
            self.inventory[key] = before
            quantity = min(
                self.random.randint(1, 5),
                before,
            )

        after = before - quantity

        self.inventory[key] = after

        gross = quantity * product["unit_price_cents"]
        eligible_for_promotion = (
            gross >= promotion["minimum_purchase_cents"]
        )
        discount_percentage = (
            promotion["discount_percentage"]
            if eligible_for_promotion
            else 0
        )
        discount = int(
            gross
            * discount_percentage
            / 100
        )

        taxable = gross - discount

        tax = int(
            taxable
            * product["tax_rate"]
            / 100
        )

        total = taxable + tax

        return {
            "transaction_id": str(uuid4()),

            "transaction_timestamp": timestamp.isoformat(),

            "invoice_number": (
                "INV-"
                + uuid4().hex[:10].upper()
            ),

            "store_id": store["store_id"],
            "store_name": store["store_name"],
            "country": store["country"],
            "city": store["city"],
            "region": store["region"],

            "terminal_id": (
                f"TERM-{self.random.randint(1, 20):03d}"
            ),

            "cashier_id": (
                f"CASH-{self.random.randint(1, 100):04d}"
            ),

            "customer_id": customer["customer_id"],
            "customer_segment": customer["customer_segment"],
            "loyalty_member": customer["loyalty_member"],

            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "category": product["category"],
            "subcategory": product["subcategory"],
            "brand": product["brand"],
            "supplier_id": product["supplier_id"],

            "quantity": quantity,
            "unit_price_cents": product["unit_price_cents"],
            "discount_cents": discount,
            "tax_cents": tax,
            "total_amount_cents": total,

            "currency": product["currency"],

            "payment_method": payment["payment_method"],
            "payment_provider": payment["provider"],

            "promotion_id": promotion["promotion_id"],

            "inventory_before": before,
            "inventory_after": after,

            "created_at": timestamp.isoformat(),
        }

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        start_date: datetime,
        days: int = 60,
    ) -> list[dict]:
        """
        Generate historical transaction records.

        Parameters
        ----------
        start_date:
            First date in the historical dataset.

        days:
            Number of calendar days to simulate.
        """

        records: list[dict] = []

        for day_offset in range(days):
            current_date = (
                start_date
                + timedelta(days=day_offset)
            )

            for store in STORES:
                for product in PRODUCTS:

                    promotion = self._promotion(
                        current_date
                    )

                    expected_quantity = (
                        self._expected_quantity(
                            store=store,
                            product=product,
                            date=current_date,
                            promotion=promotion,
                        )
                    )

                    # Split daily demand into several transactions.
                    transaction_count = max(
                        1,
                        min(
                            expected_quantity,
                            self.random.randint(1, 4),
                        ),
                    )

                    remaining_quantity = (
                        expected_quantity
                    )

                    for transaction_index in range(
                        transaction_count
                    ):
                        if remaining_quantity <= 0:
                            break

                        customer = self.random.choice(
                            CUSTOMERS
                        )

                        payment = self.random.choice(
                            PAYMENT_METHODS
                        )

                        quantity = min(
                            remaining_quantity,
                            self.random.randint(1, 5),
                        )

                        remaining_quantity -= quantity

                        # Random transaction time during store hours.
                        hour = self.random.randint(
                            9,
                            21,
                        )

                        minute = self.random.randint(
                            0,
                            59,
                        )

                        second = self.random.randint(
                            0,
                            59,
                        )

                        microsecond = self.random.randint(
                            0,
                            999_999,
                        )

                        timestamp = current_date.replace(
                            hour=hour,
                            minute=minute,
                            second=second,
                            microsecond=microsecond,
                        )

                        records.append(
                            self._transaction(
                                store=store,
                                product=product,
                                customer=customer,
                                payment=payment,
                                promotion=promotion,
                                timestamp=timestamp,
                                quantity=quantity,
                            )
                        )

        records.sort(
            key=lambda record: record[
                "transaction_timestamp"
            ]
        )

        return records

    # ------------------------------------------------------------------
    # CSV
    # ------------------------------------------------------------------

    def to_csv(
        self,
        path: str | Path,
        start_date: datetime,
        days: int = 60,
    ) -> Path:
        """
        Generate historical transactions and write them to CSV.
        """

        records = self.generate(
            start_date=start_date,
            days=days,
        )

        if not records:
            raise ValueError(
                "Historical generator produced no records."
            )

        path = Path(path)

        ensure_directory(path.parent)

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=records[0].keys(),
            )

            writer.writeheader()
            writer.writerows(records)

        logger.success(
            f"Generated {len(records):,} historical "
            f"transactions at {path}"
        )

        return path

    # ------------------------------------------------------------------
    # MinIO
    # ------------------------------------------------------------------

    def upload_to_minio(
        self,
        path: str | Path,
        object_name: str = (
            "landing/pos/"
            "historical_pos_180d.csv"
        ),
    ) -> None:
        """
        Upload generated historical data to MinIO.
        """

        minio_client = MinIOClient()

        minio_client.upload_file(
            object_name=object_name,
            file_path=str(path),
        )

        logger.success(
            "Uploaded historical POS data to MinIO: "
            f"{object_name}"
        )


def main() -> None:
    """
    Generate 180 days of historical POS data.

    The date range is explicitly controlled instead of using
    datetime.utcnow() so the dataset is reproducible.
    """

    generator = HistoricalPOSGenerator(
        seed=42
    )

    #  The Correct Code
    output_path = Path("storage") / "landing" / "historical_pos_180d.csv"


    # 180-day history ending approximately before the
    # current development period.
    end_date = datetime(2026, 8, 12)

    start_date = (
        end_date
        - timedelta(days=179)
    )

    generator.to_csv(
        path=output_path,
        start_date=start_date,
        days=180,
    )

    generator.upload_to_minio(
        path=output_path,
    )


if __name__ == "__main__":
    main()