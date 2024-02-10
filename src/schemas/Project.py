from typing import List, Optional
from pydantic import BaseModel

class ProjectSchema(BaseModel):
    name: str
    host: Optional[str]
    token: Optional[str]
    git_username: Optional[str]
    namespace: Optional[str]

class ProjectAdminSchema(BaseModel):
    email: str
    name: str
    host: Optional[str]
    token: Optional[str]
    git_username: Optional[str]
    namespace: Optional[str]

class ProjectTransferSchema(BaseModel):
    email: str