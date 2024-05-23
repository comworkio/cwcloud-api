from pydantic import BaseModel, EmailStr

class DeviceSchema(BaseModel):
    typeobject_id: str
    username: EmailStr
