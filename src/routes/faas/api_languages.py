from fastapi import APIRouter, Depends, Response
from typing import Annotated

from controllers.faas.languages import get_supported_languages
from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "faas-language"
_counter = create_counter("faas_language_api", "FaaS language API counter")

@router.get("/languages")
def find_all_languages(response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)]):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        results = get_supported_languages()
        response.status_code = results['code']
        return results
