from urllib.error import HTTPError
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from database.postgres_db import get_db
from utils.provider import get_provider_instances_pricing
from utils.observability.cid import get_current_cid
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "pricing"
_counter = create_counter("pricing_api", "Pricing API counter")

@router.get("/{provider}/pricing")
def get(provider: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        try:
            prices = get_provider_instances_pricing(provider)
            return {
                'status': 'ok',
                'prices': prices
            }
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg, 
                'i18n_code': e.headers["i18n_code"],
                'cid': get_current_cid()
            }, status_code = e.code)
