from typing import Annotated, Literal
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from schemas.User import UserSchema
from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from controllers.environment import get_environment, get_environments
from controllers.admin.admin_environment import admin_get_environments, admin_get_environment
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method
from utils.permission import check_permissions

router = APIRouter()

_span_prefix = "env"
_counter = create_counter("environment_api", "Environment API counter")

@router.get("/all")
def get_all_environments(current_user: Annotated[UserSchema, Depends(get_current_active_user)], type: Literal['vm','k8s', 'all'] = "vm", db: Session = Depends(get_db)):
    check_permissions(current_user, type, db)
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        if current_user.is_admin:
            return admin_get_environments(type, db)
        return get_environments(type, db)

@router.get("/{environment_id}")
def get_environment_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], environment_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix)):
        increment_counter(_counter, Method.GET)
        if current_user.is_admin:
            return admin_get_environment(environment_id, db)

        return get_environment(current_user, environment_id, db)
