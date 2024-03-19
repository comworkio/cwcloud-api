from typing import Optional
from pydantic import BaseModel

class PaymentSchema(BaseModel):
    invoice_id: str
    voucher_id: Optional[str]

class PaymentRelaunchSchema(BaseModel):
    invoice_id: str
