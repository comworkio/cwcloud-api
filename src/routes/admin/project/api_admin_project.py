from fastapi import Depends, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Project import ProjectAdminSchema, ProjectTransferSchema
from middleware.auth_guard import admin_required
from controllers.admin.admin_project import admin_add_project, admin_get_project, admin_get_project_by_name, admin_get_project_by_url, admin_get_projects, admin_get_user_projects, admin_remove_project, admin_remove_project_by_name, admin_remove_project_by_url, admin_transfer_project

router = APIRouter()

@router.post("")
def add_project(current_user: Annotated[UserSchema, Depends(admin_required)], payload: ProjectAdminSchema, db: Session = Depends(get_db)):
    return admin_add_project(current_user, payload, db)

@router.get("")
def get_all_projects(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    return admin_get_projects(current_user, db)


@router.post("/{project_id}/transfer")
def transfer_project(current_user: Annotated[UserSchema, Depends(admin_required)], project_id: str, payload: ProjectTransferSchema, db: Session = Depends(get_db)):
    return admin_transfer_project(current_user, project_id, payload, db)

@router.get("/{project_id}")
def get_project_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], project_id: str, db: Session = Depends(get_db)):
    return admin_get_project(current_user, project_id, db)

@router.delete("/{project_id}")
def delete_project_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], project_id: str, db: Session = Depends(get_db)):
    return admin_remove_project(current_user, project_id, db)

@router.get("/name/{project_name}")
def get_project_by_name(current_user: Annotated[UserSchema, Depends(admin_required)], project_name: str, db: Session = Depends(get_db)):
    return admin_get_project_by_name(current_user, project_name, db)

@router.delete("/name/{project_name}")
def delete_project_by_name(current_user: Annotated[UserSchema, Depends(admin_required)], project_name: str, db: Session = Depends(get_db)):
    return admin_remove_project_by_name(current_user, project_name, db)

@router.get("/url/{project_url}")
def get_project_by_url(current_user: Annotated[UserSchema, Depends(admin_required)], project_url: str, db: Session = Depends(get_db)):
    return admin_get_project_by_url(current_user, project_url, db)

@router.delete("/url/{project_url}")
def delete_project_by_url(current_user: Annotated[UserSchema, Depends(admin_required)], project_url: str, db: Session = Depends(get_db)):
    return admin_remove_project_by_url(current_user, project_url, db)

@router.get("/user/{user_id}")
def get_all_user_projects(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    return admin_get_user_projects(current_user, user_id, db)
