from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class MQTTCertificates(BaseModel):
    iot_hub_certificate: Optional[str]
    device_certificate: Optional[str]
    device_key_certificate: Optional[str]

class CallbackContent(BaseModel):
    type: str = Field(examples=["http", "websocket", "mqtt"])
    endpoint: str
    token: Optional[str]
    client_id: Optional[str]
    user_data: Optional[str]
    username: Optional[str]
    password: Optional[str]
    port: Optional[str]
    subscription: Optional[str]
    qos: Optional[str]
    topic: Optional[str]
    certificates_are_required: bool = Field(default=False)
    certificates: Optional[MQTTCertificates]

class FunctionContent(BaseModel):
    code: str = Field(examples=['function foo(arg): {return "bar " + arg;}'])
    blockly: Optional[str]
    language: str = Field(examples=["javascript", "python", "go", "bash"])
    name: str
    args: List[str]
    callbacks: Optional[List[CallbackContent]]
    regexp: Optional[str]
    env: Optional[Dict[str, str]]
