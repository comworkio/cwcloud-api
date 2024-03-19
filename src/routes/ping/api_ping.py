from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database.postgres_db import get_db

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "ping"
_counter = create_counter("ping_api", "Ping API counter")

@router.get("")
def get_ping(db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return {
            'status': 'ok',
            'alive': True
        }
