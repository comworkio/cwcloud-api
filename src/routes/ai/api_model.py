from typing import Annotated
from fastapi import Depends, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

from schemas.User import UserSchema
from middleware.auth_guard import get_current_active_user
from middleware.cwaiapi_guard import cwaiapi_required
from controllers.ai.model import load

from utils.ai.default_values import get_all_models
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "ai-models"
_counter = create_counter("ai_model_api", "CW AI Model API counter")

@router.get("/models")
def get_model(current_user: Annotated[UserSchema, Depends(get_current_active_user)], cwai: Annotated[str, Depends(cwaiapi_required)]):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return {
            'status': 'ok',
            'models': get_all_models()
        }

@router.get("/model/{model}")
def load_model(model: str, current_user: Annotated[UserSchema, Depends(get_current_active_user)], cwai: Annotated[str, Depends(cwaiapi_required)], bt: BackgroundTasks):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET, Action.DOWNLOAD)
        result = load(model, bt)
        return JSONResponse(content = result, status_code = result['http_status'])
