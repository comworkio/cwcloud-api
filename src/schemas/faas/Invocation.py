from pydantic import BaseModel
from typing import Optional

from schemas.faas.InvocationContent import InvocationContent

class Invocation(BaseModel):
    invoker_id: Optional[int]
    content: InvocationContent

class CompletedInvocation(Invocation):
    id: Optional[str]
    invoker_username: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
