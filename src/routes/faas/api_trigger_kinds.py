from fastapi import APIRouter, Depends, Response
from typing import Annotated

from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema
from controllers.faas.trigger_kinds import get_all_triggers_kinds

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "faas-trigger-kinds"

@router.get("/trigger_kinds")
def get_all_kinds(response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)]):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        results = get_all_triggers_kinds()
        response.status_code = results['code']
        return results
