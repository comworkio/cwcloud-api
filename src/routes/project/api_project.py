from fastapi import Depends, APIRouter
from typing import Annotated, Literal
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Project import ProjectSchema, ProjectTransferSchema
from middleware.auth_guard import get_current_active_user
from controllers.project import add_project, delete_project, delete_project_by_name, delete_project_by_url, get_project, get_project_by_name, get_project_by_url, get_projects, transfer_project

router = APIRouter()

@router.get("")
def get_all_projects(current_user: Annotated[UserSchema, Depends(get_current_active_user)],type: Literal['vm','k8s','all'] = "all" , db: Session = Depends(get_db)):
    return get_projects(current_user, db, type)

@router.post("")
def add_new_project(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: ProjectSchema, db: Session = Depends(get_db)):
    return add_project(current_user, payload, db)

@router.get("/{projectId}")
def get_project_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], projectId: str, db: Session = Depends(get_db)):
    return get_project(current_user, projectId, db)

@router.delete("/{projectId}")
def delete_project_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], projectId: str, db: Session = Depends(get_db)):
    return delete_project(current_user, projectId, db)

@router.post("/{project_id}/transfer")
def transfer_project_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: ProjectTransferSchema, project_id: str, db: Session = Depends(get_db)):
    return transfer_project(current_user, payload, project_id, db)

@router.get("/name/{project_name}")
def get_the_project_by_name(current_user: Annotated[UserSchema, Depends(get_current_active_user)], project_name: str, db: Session = Depends(get_db)):
    return get_project_by_name(current_user, project_name, db)

@router.delete("/name/{project_name}")
def delete_the_project_by_name(current_user: Annotated[UserSchema, Depends(get_current_active_user)], project_name: str, db: Session = Depends(get_db)):
    return delete_project_by_name(current_user, project_name, db)

@router.get("/url/{project_url:path}")
def get_the_project_by_url(current_user: Annotated[UserSchema, Depends(get_current_active_user)], project_url: str, db: Session = Depends(get_db)):
    return get_project_by_url(current_user, project_url, db)

@router.delete("/url/{project_url:path}")
def delete_the_project_by_url(current_user: Annotated[UserSchema, Depends(get_current_active_user)], project_url: str, db: Session = Depends(get_db)):
    return delete_project_by_url(current_user, project_url, db)
