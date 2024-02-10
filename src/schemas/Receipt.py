from typing import Optional
from pydantic import BaseModel

class ReceiptDownloadSchema(BaseModel):
    email: Optional[str]
    user_id: Optional[int]
