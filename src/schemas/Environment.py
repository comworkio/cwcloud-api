from pydantic import BaseModel
from typing import Optional, List, Union
from schemas.Kubernetes import ExternalChart
class EnvironmentSchema(BaseModel):
    name: str
    path: str
    description: Optional[str] = None
    environment_template: Optional[str] = None
    doc_template: Optional[str] = None
    roles: Union[str, List[str]]
    subdomains: Optional[Union[str, List[str]]] = []
    is_private: bool
    logo_url: Optional[str] = None

class K8SEnvironmentSchema(BaseModel):
    name: str
    description: str
    logo_url: str
    is_private: bool
    charts: str
    external_charts: Optional[list[ExternalChart]] = None
