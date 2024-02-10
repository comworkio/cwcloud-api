from pydantic import BaseModel

class ApiKeysSchema(BaseModel):
    name: str

class ApiKeysVerificationSchema(BaseModel):
    access_key: str
    secret_key: str
