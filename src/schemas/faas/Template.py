from pydantic import BaseModel
from typing import List

class FunctionTemplate(BaseModel):
    args: List[str]
    language: str
