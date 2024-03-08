from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from schemas.Project import ProjectAdminSchema, ProjectTransferSchema
from controllers.admin.admin_project import admin_add_project, admin_get_project, admin_get_project_by_name, admin_get_project_by_url, admin_get_projects, admin_get_user_projects, admin_remove_project, admin_remove_project_by_name, admin_remove_project_by_url, admin_transfer_project

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-project"

@router.post("")
def add_project(current_user: Annotated[UserSchema, Depends(admin_required)], payload: ProjectAdminSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        return admin_add_project(payload, db)

@router.get("")
def get_all_projects(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return admin_get_projects(db)

@router.post("/{project_id}/transfer")
def transfer_project(current_user: Annotated[UserSchema, Depends(admin_required)], project_id: str, payload: ProjectTransferSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-move".format(_span_prefix)):
        return admin_transfer_project(project_id, payload, db)

@router.get("/{project_id}")
def get_project_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], project_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return admin_get_project(project_id, db)

@router.delete("/{project_id}")
def delete_project_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], project_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        return admin_remove_project(project_id, db)

@router.get("/name/{project_name}")
def get_project_by_name(current_user: Annotated[UserSchema, Depends(admin_required)], project_name: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-byname".format(_span_prefix)):
        return admin_get_project_by_name(project_name, db)

@router.delete("/name/{project_name}")
def delete_project_by_name(current_user: Annotated[UserSchema, Depends(admin_required)], project_name: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete-byname".format(_span_prefix)):
        return admin_remove_project_by_name(project_name, db)

@router.get("/url/{project_url}")
def get_project_by_url(current_user: Annotated[UserSchema, Depends(admin_required)], project_url: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-byurl".format(_span_prefix)):
        return admin_get_project_by_url(project_url, db)

@router.delete("/url/{project_url}")
def delete_project_by_url(current_user: Annotated[UserSchema, Depends(admin_required)], project_url: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete-byurl".format(_span_prefix)):
        return admin_remove_project_by_url(project_url, db)

@router.get("/user/{user_id}")
def get_all_user_projects(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-byuser".format(_span_prefix)):
        return admin_get_user_projects(user_id, db)
