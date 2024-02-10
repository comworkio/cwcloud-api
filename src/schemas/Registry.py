import os

from typing import List, Optional
from pydantic import BaseModel

from utils.provider import get_provider_infos

class RegistrySchema(BaseModel):
    name: str
    email: str
    type: str


class RegistryUpdateSchema(BaseModel):
    email: Optional[str]
    update_creds: Optional[bool] = False
