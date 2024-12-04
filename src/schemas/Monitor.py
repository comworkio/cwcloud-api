from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from enum import Enum

class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"

class MonitorType(str, Enum):
    HTTP = "http"

class Header(BaseModel):
    name: str
    value: str

class BaseMonitorSchema(BaseModel):
    type: MonitorType = Field(..., description="Type of monitor")
    name: str
    family: Optional[str] = None
    url: HttpUrl
    method: HttpMethod = Field(default=HttpMethod.GET, description="HTTP method")
    expected_http_code: str = Field(default='20*')
    body: Optional[str] = Field(None, description="Request body for POST/PUT requests")
    expected_contain: Optional[str] = Field(None, description="Expected content in the HTTP response body")
    timeout: int = Field(default=30, gt=0, le=300)
    username: Optional[str] = None
    password: Optional[str] = None
    headers: List[Header] = Field(default_factory=list, description="Optional headers for the HTTP request")

class MonitorSchema(BaseMonitorSchema):
    pass

class AdminMonitorSchema(BaseMonitorSchema):
    user_id: int
