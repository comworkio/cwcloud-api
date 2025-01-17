from typing import List, Optional
from pydantic import BaseModel

class RegistrySchema(BaseModel):
    name: str
    email: str
    type: str


class RegistryUpdateSchema(BaseModel):
    email: Optional[str]
    update_creds: Optional[bool] = False
