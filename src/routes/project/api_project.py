from typing import Annotated, Literal
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Project import ProjectSchema, ProjectTransferSchema
from middleware.auth_guard import get_current_active_user
from controllers.project import add_project, delete_project, delete_project_by_name, delete_project_by_url, get_project, get_project_by_name, get_project_by_url, get_projects, transfer_project

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method
from utils.permission import check_permissions

router = APIRouter()

_span_prefix = "project"
_counter = create_counter("project_api", "Project API counter")

@router.get("")
def get_all_projects(current_user: Annotated[UserSchema, Depends(get_current_active_user)], type: Literal['vm','k8s', 'all'] = "vm", db: Session = Depends(get_db)):
    check_permissions(current_user, type, db)
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return get_projects(current_user, type, db)

@router.post("")
def add_new_project(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: ProjectSchema, db: Session = Depends(get_db)):
    check_permissions(current_user, payload.type, db)
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return add_project(current_user, payload, db)

@router.get("/{projectId}")
def get_project_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], projectId: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_project(current_user, projectId, db)

@router.delete("/{projectId}")
def delete_project_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], projectId: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return delete_project(current_user, projectId, db)

@router.post("/{project_id}/transfer")
def transfer_project_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: ProjectTransferSchema, project_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST, Action.MOVE)):
        increment_counter(_counter, Method.POST, Action.MOVE)
        return transfer_project(current_user, payload, project_id, db)

@router.get("/name/{project_name}")
def get_the_project_by_name(current_user: Annotated[UserSchema, Depends(get_current_active_user)], project_name: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.BYNAME)):
        increment_counter(_counter, Method.GET, Action.BYNAME)
        return get_project_by_name(current_user, project_name, db)

@router.delete("/name/{project_name}")
def delete_the_project_by_name(current_user: Annotated[UserSchema, Depends(get_current_active_user)], project_name: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE, Action.BYNAME)):
        increment_counter(_counter, Method.DELETE, Action.BYNAME)
        return delete_project_by_name(current_user, project_name, db)

@router.get("/url/{project_url:path}")
def get_the_project_by_url(current_user: Annotated[UserSchema, Depends(get_current_active_user)], project_url: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.BYURL)):
        increment_counter(_counter, Method.GET, Action.BYURL)
        return get_project_by_url(current_user, project_url, db)

@router.delete("/url/{project_url:path}")
def delete_the_project_by_url(current_user: Annotated[UserSchema, Depends(get_current_active_user)], project_url: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE, Action.BYURL)):
        increment_counter(_counter, Method.DELETE, Action.BYURL)
        return delete_project_by_url(current_user, project_url, db)
