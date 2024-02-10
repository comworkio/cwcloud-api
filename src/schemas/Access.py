from pydantic import BaseModel

class AccessSchema(BaseModel):
    email: str
    object_id: str
    object_type: str
