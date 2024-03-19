from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from schemas.Project import ProjectAdminSchema, ProjectTransferSchema
from controllers.admin.admin_project import admin_add_project, admin_get_project, admin_get_project_by_name, admin_get_project_by_url, admin_get_projects, admin_get_user_projects, admin_remove_project, admin_remove_project_by_name, admin_remove_project_by_url, admin_transfer_project

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "adm-project"
_counter = create_counter("adm_project_api", "Admin project API counter")

@router.post("")
def add_project(current_user: Annotated[UserSchema, Depends(admin_required)], payload: ProjectAdminSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return admin_add_project(payload, db)

@router.get("")
def get_all_projects(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return admin_get_projects(db)

@router.post("/{project_id}/transfer")
def transfer_project(current_user: Annotated[UserSchema, Depends(admin_required)], project_id: str, payload: ProjectTransferSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.MOVE)):
        increment_counter(_counter, Method.POST, Action.MOVE)
        return admin_transfer_project(project_id, payload, db)

@router.get("/{project_id}")
def get_project_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], project_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return admin_get_project(project_id, db)

@router.delete("/{project_id}")
def delete_project_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], project_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return admin_remove_project(project_id, db)

@router.get("/name/{project_name}")
def get_project_by_name(current_user: Annotated[UserSchema, Depends(admin_required)], project_name: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.BYNAME)):
        increment_counter(_counter, Method.GET, Action.BYNAME)
        return admin_get_project_by_name(project_name, db)

@router.delete("/name/{project_name}")
def delete_project_by_name(current_user: Annotated[UserSchema, Depends(admin_required)], project_name: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE, Action.BYNAME)):
        increment_counter(_counter, Method.DELETE, Action.BYNAME)
        return admin_remove_project_by_name(project_name, db)

@router.get("/url/{project_url}")
def get_project_by_url(current_user: Annotated[UserSchema, Depends(admin_required)], project_url: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.BYURL)):
        increment_counter(_counter, Method.GET, Action.BYURL)
        return admin_get_project_by_url(project_url, db)

@router.delete("/url/{project_url}")
def delete_project_by_url(current_user: Annotated[UserSchema, Depends(admin_required)], project_url: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE, Action.BYURL)):
        increment_counter(_counter, Method.DELETE, Action.BYURL)
        return admin_remove_project_by_url(project_url, db)

@router.get("/user/{user_id}")
def get_all_user_projects(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.BYUSER)):
        increment_counter(_counter, Method.GET, Action.BYUSER)
        return admin_get_user_projects(user_id, db)
