from fastapi import APIRouter, Depends, Response
from typing import Annotated

from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema
from schemas.faas.Template import FunctionTemplate
from controllers.faas.templates import generate_template

router = APIRouter()

@router.post("/template")
def generate_tpl(payload: FunctionTemplate, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)]):
    result = generate_template(payload)
    response.status_code = result['code']
    return result
