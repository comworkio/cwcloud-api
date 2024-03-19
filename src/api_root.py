from fastapi import status, APIRouter

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "health"
_counter = create_counter("health_api", "Health API counter")

@router.get("", status_code = status.HTTP_200_OK)
def get_health():
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return {
            'status': 'ok',
            'alive': True
        }
