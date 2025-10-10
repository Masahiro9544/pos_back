from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal

# --- POSアプリ用スキーマ ---
class PurchaseItem(BaseModel):
    prd_id: int
    code: int
    name: str
    price: int
    quantity: int

class PurchaseRequest(BaseModel):
    items: List[PurchaseItem]
    emp_cd: Optional[str] = None

class PurchaseResponse(BaseModel):
    trd_id: int
    total_amt: int
    ttl_amt_ex_tax: int
    tax_amt: int

class TaxResponse(BaseModel):
    tax_id: int
    tax_rate: Decimal
