from typing import List, Optional
from pydantic import BaseModel

class InvoiceSchema(BaseModel):
    email: str
    from_: str
    to: str
    send: Optional[bool] = True
    preview: Optional[bool] = False

    class Config:
        fields = {
            'from_': 'from',
        }

class InvoiceUpdateSchema(BaseModel):
    status: str

class ItemModelSchema(BaseModel):
    label: str
    price: float

class InvoiceCustomSchema(BaseModel):
    email: str
    date: str
    send: Optional[bool] = True
    preview: Optional[bool] = False
    items: List[ItemModelSchema]

class InvoiceDownloadSchema(BaseModel):
    email: Optional[str]
    user_id: Optional[int]

class InvoiceEditionSchema(BaseModel):
    ref: str
    new_ref: str
    email: str
