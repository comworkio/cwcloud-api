from pydantic import BaseModel
from typing import Optional, List, Union
from schemas.Kubernetes import ExternalChart


class GeneralEnvironmentSchema(BaseModel):
    name: str
    path: str
    args: Optional[list[str]] = None
    description: Optional[str] = None
    environment_template: Optional[str] = None
    doc_template: Optional[str] = None
    subdomains: Optional[Union[str, List[str]]] = []
    is_private: bool
    logo_url: Optional[str] = None,


class EnvironmentSchema(GeneralEnvironmentSchema):
    roles: Union[str, List[str]]


class K8SEnvironmentSchema(GeneralEnvironmentSchema):
    charts: str
    external_charts: Optional[list[ExternalChart]] = None
