from controllers.iot.data import add_data
from fastapi import APIRouter, Depends
from middleware.auth_guard import get_current_not_mandatory_user, get_user_authentication
from schemas.UserAuthentication import UserAuthentication
from schemas.iot.Data import DataSchema
from sqlalchemy.orm import Session
from typing import Annotated
from database.postgres_db import get_db
from schemas.User import UserSchema
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "iot-data"
_counter = create_counter("iot_data_api", "IoT data API counter")

@router.post("/data")
def create_data(current_user: Annotated[UserSchema, Depends(get_current_not_mandatory_user)], user_auth: Annotated[UserAuthentication, Depends(get_user_authentication)], payload: DataSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return add_data(current_user, user_auth, payload, db)
