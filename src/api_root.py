from fastapi import status, APIRouter

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "health"

@router.get("", status_code = status.HTTP_200_OK)
def get_health():
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return {
            'status': 'ok',
            'alive': True
        }
