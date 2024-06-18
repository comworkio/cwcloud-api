from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, BackgroundTasks

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Instance import InstanceUpdateSchema, InstanceAttachSchema, InstanceProvisionSchema
from middleware.auth_guard import get_current_active_user
from middleware.daasapi_guard import daasapi_required
from controllers.instance import attach_instance, get_instance, get_instances, provision_instance, update_instance, remove_instance

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "instance"
_counter = create_counter("instance_api", "Instance API counter")

@router.get("/{provider}/{region}")
def get_all_instances(current_user: Annotated[UserSchema, Depends(get_current_active_user)], daas: Annotated[UserSchema, Depends(daasapi_required)], provider: str, region: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return get_instances(current_user, provider, region, db)

@router.get("/{provider}/{region}/{instance_id}")
def get_instance_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], daas: Annotated[UserSchema, Depends(daasapi_required)], provider: str, region: str, instance_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_instance(current_user, provider, region, instance_id, db)

@router.delete("/{provider}/{region}/{instance_id}")
def delete_instance(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(get_current_active_user)], daas: Annotated[UserSchema, Depends(daasapi_required)], provider: str, region: str, instance_id: str , db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return remove_instance(current_user, provider, region, instance_id, db, bt)

@router.patch("/{provider}/{region}/{instance_id}")
def update_instance_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], daas: Annotated[UserSchema, Depends(daasapi_required)], payload: InstanceUpdateSchema, provider: str, region: str, instance_id: str , db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.PATCH)):
        increment_counter(_counter, Method.PATCH)
        return update_instance(current_user, payload, provider, region, instance_id, db)

@router.post("/{provider}/{region}/{zone}/attach/{project_id}")
def attach_new_instance(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(get_current_active_user)], daas: Annotated[UserSchema, Depends(daasapi_required)], provider: str, region: str, zone: str, project_id: str, payload: InstanceAttachSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ATTACH)):
        increment_counter(_counter, Method.GET, Action.ATTACH)
        return attach_instance(bt, current_user, provider, region, zone, project_id, payload, db)

@router.post("/{provider}/{region}/{zone}/provision/{environment}")
def add_new_instance(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(get_current_active_user)], daas: Annotated[UserSchema, Depends(daasapi_required)], payload: InstanceProvisionSchema, provider: str, region: str, zone: str, environment: str , db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return provision_instance(current_user, payload, provider, region, zone, environment, db, bt)
