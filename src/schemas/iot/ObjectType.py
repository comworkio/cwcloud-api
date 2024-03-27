from pydantic import BaseModel
from typing import Optional

class ObjectTypeContent(BaseModel):
    public: bool
    decoding_function: str
    triggers: list[str]

class ObjectTypeSchema(BaseModel):
    content: ObjectTypeContent

class AdminObjectTypeSchema(BaseModel):
    content : ObjectTypeContent
    user_id: Optional[int]
