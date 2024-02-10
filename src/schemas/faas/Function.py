from pydantic import BaseModel
from typing import Optional

from schemas.faas.FunctionContent import FunctionContent

class BaseFunction(BaseModel):
    is_public: Optional[bool]
    owner_id: Optional[int]
    content: FunctionContent

class Function(BaseFunction):
    id: Optional[str]
    owner_username: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
