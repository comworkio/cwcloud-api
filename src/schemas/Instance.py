import os

from typing import Optional
from pydantic import BaseModel

from utils.dns_zones import get_first_dns_zone_doc
from utils.provider import get_provider_infos

class InstanceUpdateSchema(BaseModel):
    status: Optional[str]
    is_protected: Optional[bool]

class InstanceAttachSchema(BaseModel):
    name: str = "Instance Name"
    type: str = get_provider_infos(os.environ['DEFAULT_PROVIDER'], 'instance_types')[0]
    debug: Optional[bool] = True

class InstanceProvisionSchema(BaseModel):
    name: str = "Instance Name"
    email: Optional[str]
    project_id: Optional[str]
    project_name: Optional[str]
    project_url: Optional[str]
    debug: Optional[str]
    type: str = get_provider_infos(os.environ['DEFAULT_PROVIDER'], 'instance_types')[0]
    root_dns_zone: str = get_first_dns_zone_doc()

