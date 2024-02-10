from pydantic import BaseModel

class InvocationArgument(BaseModel):
    key: str
    value: str
