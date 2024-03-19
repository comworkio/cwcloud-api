from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from database.postgres_db import get_db

from utils.provider import exist_provider, get_provider_infos
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method
from utils.observability.cid import get_current_cid

router = APIRouter()

_span_prefix = "instance-types"
_counter = create_counter("instance_type_api", "Instance type API counter")

@router.get("/{provider}/instance_types")
def get_instance_types(provider: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        if not exist_provider(provider):
            return JSONResponse(content = {
                'status': 'ko',
                'error': "provider doesn't exist", 
                'i18n_code': '504',
                'cid': get_current_cid()
            }, status_code = 404)
        return {
            "status": "ok",
            "types": get_provider_infos(provider, "instance_types")
        }
