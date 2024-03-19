from fastapi import APIRouter, Depends, Response
from typing import Annotated

from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema
from controllers.faas.trigger_kinds import get_all_triggers_kinds

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "faas-trigger-kind"
_counter = create_counter("faas_trigger_kind_api", "FaaS trigger kind API counter")

@router.get("/trigger_kinds")
def get_all_kinds(response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)]):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        results = get_all_triggers_kinds()
        response.status_code = results['code']
        return results
