from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class FunctionContent(BaseModel):
    code: str = Field(examples=['function foo(arg): {return "bar " + arg;}'])
    blockly: Optional[str]
    language: str = Field(examples=["javascript", "python", "go", "bash"])
    name: str
    args: List[str]
    callback_url: Optional[str]
    callback_authorization_header: Optional[str]
    regexp: Optional[str]
    env: Optional[Dict[str, str]]
