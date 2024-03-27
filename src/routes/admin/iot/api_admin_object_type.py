from controllers.admin.iot.admin_object_type import add_object_type, delete_object_type, get_object_types, get_object_type, update_object_type
from fastapi import APIRouter, Depends
from middleware.auth_guard import admin_required
from schemas.iot.ObjectType import AdminObjectTypeSchema
from sqlalchemy.orm import Session
from typing import Annotated
from database.postgres_db import get_db
from schemas.User import UserSchema
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "adm-iot-object-type"
_counter = create_counter("adm_iot_object_type_api", "Admin IoT object type API counter")

@router.post("/object-type")
def create_object_type(current_user: Annotated[UserSchema, Depends(admin_required)], payload: AdminObjectTypeSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return add_object_type(current_user, payload, db)
    
@router.get("/object-types")
def get_all_object_types(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_object_types(current_user, db)
    
@router.get("/object-type/{object_type_id}")
def get_object_type_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], object_type_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_object_type(current_user, object_type_id, db)
    
@router.put("/object-type/{object_type_id}")
def update_object_type_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], object_type_id: str, payload: AdminObjectTypeSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.PUT)):
        increment_counter(_counter, Method.PUT)
        return update_object_type(current_user, object_type_id, payload, db)
    
@router.delete("/object-type/{object_type_id}")
def delete_object_type_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], object_type_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return delete_object_type(current_user, object_type_id, db)
