from controllers.admin.iot.admin_data import get_datas, get_numeric_data, get_string_data
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

_span_prefix = "adm-iot-data"
_counter = create_counter("adm_iot_data_api", "Admin IoT data API counter")

@router.get("/data")
def get_all_data(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_datas(current_user, db)

@router.get("/data/numeric")
def get_all_numeric_data(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_numeric_data(current_user, db)
    
@router.get("/data/string")
def get_all_string_data(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_string_data(current_user, db)
