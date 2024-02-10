from pydantic import BaseModel

class MFASchema(BaseModel):
    code: str

class MFARegister2faSchema(BaseModel):
    code: str
    otp_code: str
