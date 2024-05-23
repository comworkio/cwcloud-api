from pydantic import BaseModel, Field
class DataSchema(BaseModel):
    device_id: str
    content: str
