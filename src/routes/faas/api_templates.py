from fastapi import APIRouter, Depends, Response
from typing import Annotated

from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema
from schemas.faas.Template import FunctionTemplate
from controllers.faas.templates import generate_template

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "faas-template"

@router.post("/template")
def generate_tpl(payload: FunctionTemplate, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)]):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        result = generate_template(payload)
        response.status_code = result['code']
        return result
