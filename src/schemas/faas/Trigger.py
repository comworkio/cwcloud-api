from pydantic import BaseModel
from typing import Optional

from schemas.faas.TriggerContent import TriggerContent

class Trigger(BaseModel):
    kind: str
    owner_id: Optional[int]
    content: TriggerContent

class CompletedTrigger(Trigger):
    id: Optional[str]
    owner_username: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
