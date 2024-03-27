from controllers.iot.object_type import add_object_type, delete_object_type, get_object_type, get_object_types, update_object_type
from fastapi import APIRouter, Depends
from middleware.iotapi_guard import iotapi_required
from schemas.iot.ObjectType import ObjectTypeSchema
from sqlalchemy.orm import Session
from typing import Annotated
from database.postgres_db import get_db
from schemas.User import UserSchema
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "iot-object-type"
_counter = create_counter("iot_object_type_api", "IoT object type API counter")

@router.post("/object-type")
def create_object_type(current_user: Annotated[UserSchema, Depends(iotapi_required)], payload: ObjectTypeSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return add_object_type(current_user, payload, db)
    
@router.get("/object-types")
def get_user_object_types(current_user: Annotated[UserSchema, Depends(iotapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_object_types(current_user, db)
    
@router.get("/object-type/{object_type_id}")
def get_user_object_type(current_user: Annotated[UserSchema, Depends(iotapi_required)], object_type_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_object_type(current_user, object_type_id, db)
    
@router.put("/object-type/{object_type_id}")
def update_user_object_type(current_user: Annotated[UserSchema, Depends(iotapi_required)], object_type_id: str, payload: ObjectTypeSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.PUT)):
        increment_counter(_counter, Method.PUT)
        return update_object_type(current_user, object_type_id, payload, db)
    
@router.delete("/object-type/{object_type_id}")
def delete_user_object_type(current_user: Annotated[UserSchema, Depends(iotapi_required)], object_type_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return delete_object_type(current_user, object_type_id, db)
