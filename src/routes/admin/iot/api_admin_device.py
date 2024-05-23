from controllers.admin.iot.admin_device import get_devices, delete_device
from fastapi import APIRouter, Depends
from middleware.auth_guard import admin_required
from sqlalchemy.orm import Session
from typing import Annotated
from database.postgres_db import get_db
from schemas.User import UserSchema
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "adm-iot-device"
_counter = create_counter("adm_iot_device_api", "Admin IoT device API counter")

@router.get("/devices")
def get_all_devices(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_devices(db)

@router.delete("/device/{device_id}")
def remove_device(current_user: Annotated[UserSchema, Depends(admin_required)], device_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return delete_device(device_id, db)
