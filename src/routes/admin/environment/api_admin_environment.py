from fastapi import Depends, APIRouter, File, UploadFile
from typing import Annotated
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Environment import EnvironmentSchema
from middleware.auth_guard import admin_required
from controllers.admin.admin_environment import admin_add_environment, admin_get_environment, admin_get_environments, admin_get_roles, admin_remove_environment, admin_update_environment, admin_export_environment, admin_import_environment

router = APIRouter()

@router.get("/roles")
def get_roles(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    return admin_get_roles(current_user)

@router.get("/all")
def get_all_environments(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    return admin_get_environments(current_user, db)

@router.get("/{environmentId}/export")
def export_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environmentId: str, db: Session = Depends(get_db)):
    return admin_export_environment(current_user, environmentId, db)

@router.get("/{environmentId}")
def get_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environmentId: str, db: Session = Depends(get_db)):
    return admin_get_environment(current_user, environmentId, db)

@router.put("/{environmentId}")
def update_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environmentId: str, payload: EnvironmentSchema, db: Session = Depends(get_db)):
    return admin_update_environment(current_user, environmentId, payload, db)

@router.delete("/{environmentId}")
def delete_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environmentId: str, db: Session = Depends(get_db)):
    return admin_remove_environment(current_user, environmentId, db)

@router.post("/import")
def import_environment(current_user: Annotated[UserSchema, Depends(admin_required)], env: UploadFile = File(...), db: Session = Depends(get_db)):
    return admin_import_environment(current_user, env, db)

@router.post("")
def add_environment(current_user: Annotated[UserSchema, Depends(admin_required)], payload: EnvironmentSchema, db: Session = Depends(get_db)):
    return admin_add_environment(current_user, payload, db)
