from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, status, APIRouter

from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from schemas.User import UserSchema

from utils.dns_zones import get_dns_zones
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "dns-zones"

@router.get("", status_code = status.HTTP_200_OK)
def get_all_dns_zones(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return {
            "status": "ok",
            "zones": get_dns_zones()
        }
