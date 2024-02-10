from pydantic import BaseModel

class ContactSchema(BaseModel):
    email: str
    subject: str
    message: str
