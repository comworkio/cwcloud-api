from controllers.iot.device import add_device, confirm_device_by_token, delete_user_device_by_id, get_user_device_by_id, get_user_devices
from fastapi import APIRouter, Depends
from middleware.auth_guard import get_current_not_mandatory_user
from schemas.iot.Device import DeviceSchema
from sqlalchemy.orm import Session
from typing import Annotated
from database.postgres_db import get_db
from schemas.User import UserSchema
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "iot-device"
_counter = create_counter("iot_device_api", "IoT device API counter")

@router.post("/device")
def create_device(current_user: Annotated[UserSchema, Depends(get_current_not_mandatory_user)], payload: DeviceSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return add_device(current_user, payload, db)

@router.post("/device-confirmation/{token}")
def confirm_device(token: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return confirm_device_by_token(token, db)
    
@router.get("/devices")
def get_devices(current_user: Annotated[UserSchema, Depends(get_current_not_mandatory_user)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_user_devices(current_user, db)
    
@router.get("/device/{device_id}")
def get_device(current_user: Annotated[UserSchema, Depends(get_current_not_mandatory_user)], device_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_user_device_by_id(current_user, device_id, db)
    
@router.delete("/device/{device_id}")
def delete_device(current_user: Annotated[UserSchema, Depends(get_current_not_mandatory_user)], device_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return delete_user_device_by_id(current_user, device_id, db)
