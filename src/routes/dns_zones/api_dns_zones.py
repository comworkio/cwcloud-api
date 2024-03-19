from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, status, APIRouter

from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from schemas.User import UserSchema

from utils.dns_zones import get_dns_zones
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "dns-zones"
_counter = create_counter("dns_zones_api", "DNS zones API counter")

@router.get("", status_code = status.HTTP_200_OK)
def get_all_dns_zones(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return {
            "status": "ok",
            "zones": get_dns_zones()
        }
