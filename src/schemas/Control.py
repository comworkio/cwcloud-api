from pydantic import BaseModel

class ControlDeleteInstanceSchema(BaseModel):
    error: str

class ControlUpdateInstanceSchema(BaseModel):
    status: str
