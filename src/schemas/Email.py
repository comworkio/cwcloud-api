from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class AttachmentSchema(BaseModel):
    mime_type: str
    file_name: str
    b64: str

class EmailSchema(BaseModel):
    from_: Optional[EmailStr] = Field(None, alias="from")
    from_name: Optional[str]
    to: EmailStr
    cc: Optional[EmailStr]
    bcc: Optional[EmailStr]
    replyto: Optional[EmailStr]
    subject: str
    content: Optional[str]
    attachment: Optional[AttachmentSchema]

class EmailAdminSchema(BaseModel):
    from_: EmailStr = Field(..., alias = "from")
    from_name: Optional[str]
    to: EmailStr
    cc: Optional[EmailStr]
    bcc: Optional[EmailStr]
    replyto: Optional[EmailStr]
    subject: str
    content: Optional[str]
    attachment: Optional[AttachmentSchema]
    templated: Optional[bool] = False
