
from __future__ import annotations
import csv, random
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from ingestion.master_data.stores import STORES
from ingestion.master_data.products import PRODUCTS
from ingestion.master_data.customers import CUSTOMERS
from ingestion.master_data.payment_methods import PAYMENT_METHODS
from ingestion.master_data.promotions import PROMOTIONS
from core.logger import get_logger
from core.utils import ensure_directory

logger = get_logger(__name__)

class POSBatchGenerator:
    def __init__(self, seed:int=42):
        random.seed(seed)

    def _record(self):
        store=random.choice(STORES)
        product=random.choice(PRODUCTS)
        customer=random.choice(CUSTOMERS)
        payment=random.choice(PAYMENT_METHODS)
        promo=random.choice(PROMOTIONS)
        qty=random.randint(1,5)
        gross=qty*product["unit_price_cents"]
        discount=int(gross*promo["discount_percentage"]/100)
        taxable=gross-discount
        tax=int(taxable*product["tax_rate"]/100)
        total=taxable+tax
        before=random.randint(50,500)
        return {
            "transaction_id":str(uuid4()),
            "transaction_timestamp":datetime.utcnow().isoformat(),
            "invoice_number":"INV-"+uuid4().hex[:10].upper(),
            "store_id":store["store_id"],
            "store_name":store["store_name"],
            "country":store["country"],
            "city":store["city"],
            "region":store["region"],
            "terminal_id":f"TERM-{random.randint(1,20):03d}",
            "cashier_id":f"CASH-{random.randint(1,100):04d}",
            "customer_id":customer["customer_id"],
            "customer_segment":customer["customer_segment"],
            "loyalty_member":customer["loyalty_member"],
            "product_id":product["product_id"],
            "product_name":product["product_name"],
            "category":product["category"],
            "subcategory":product["subcategory"],
            "brand":product["brand"],
            "supplier_id":product["supplier_id"],
            "quantity":qty,
            "unit_price_cents":product["unit_price_cents"],
            "discount_cents":discount,
            "tax_cents":tax,
            "total_amount_cents":total,
            "currency":product["currency"],
            "payment_method":payment["payment_method"],
            "payment_provider":payment["provider"],
            "promotion_id":promo["promotion_id"],
            "inventory_before":before,
            "inventory_after":max(0,before-qty),
            "created_at":datetime.utcnow().isoformat()
        }

    def generate(self,n:int):
        return [self._record() for _ in range(n)]

    def to_csv(self,path:str|Path,records:int=1000):
        rows=self.generate(records)
        path=Path(path)
        ensure_directory(path.parent)
        with open(path,"w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        logger.success(f"Generated {records} records at {path}")

if __name__=="__main__":
    POSBatchGenerator().to_csv("storage/landing/pos_transactions.csv",1000)
