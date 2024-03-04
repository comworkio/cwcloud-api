from typing import Optional, Literal
from pydantic import BaseModel, Field

class ProjectSchema(BaseModel):
    name: str
    type: Optional[Literal['vm', 'k8s']] = Field('vm', description="Type of project (vm or k8s)")
    host: Optional[str]
    token: Optional[str]
    git_username: Optional[str]
    git_useremail: Optional[str]
    namespace: Optional[str]

class ProjectAdminSchema(BaseModel):
    email: str
    name: str
    type: Optional[Literal['vm', 'k8s']] = Field('vm', description="Type of project (vm or k8s)")
    host: Optional[str]
    token: Optional[str]
    git_username: Optional[str]
    git_useremail: Optional[str]
    namespace: Optional[str]

class ProjectTransferSchema(BaseModel):
    email: str