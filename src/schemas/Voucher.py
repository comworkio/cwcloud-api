from typing import Optional
from pydantic import BaseModel

class VoucherSchema(BaseModel):
    code: str

class VoucherAdminSchema(BaseModel):
    code: str
    email: str
    validity: Optional[int]
    price: float
