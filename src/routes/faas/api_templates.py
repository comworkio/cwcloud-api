from fastapi import APIRouter, Depends, Response
from typing import Annotated

from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema
from schemas.faas.Template import FunctionTemplate
from controllers.faas.templates import generate_template

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "faas-template"
_counter = create_counter("faas_template_api", "FaaS template API counter")

@router.post("/template")
def generate_tpl(payload: FunctionTemplate, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)]):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        result = generate_template(payload)
        response.status_code = result['code']
        return result
