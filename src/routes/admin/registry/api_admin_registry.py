from fastapi import Depends, APIRouter, BackgroundTasks
from typing import Annotated
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Registry import RegistrySchema, RegistryUpdateSchema
from middleware.auth_guard import admin_required
from controllers.admin.admin_registry import admin_add_registry, admin_get_registries, admin_get_registry, admin_get_user_registries, admin_refresh_registry, admin_remove_registry, admin_update_registry

router = APIRouter()

@router.post("/{provider}/{region}/provision")
def add_registry(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, payload: RegistrySchema, db: Session = Depends(get_db)):
    return admin_add_registry(current_user, provider, region, payload, db, bt)

@router.get("/{registry_id}")
def get_registry_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], registry_id: str, db: Session = Depends(get_db)):
    return admin_get_registry(current_user, registry_id, db)

@router.delete("/{registry_id}")
def delete_registry_by_id(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(admin_required)], registry_id: str, db: Session = Depends(get_db)):
    return admin_remove_registry(current_user, registry_id, db, bt)

@router.patch("/{registry_id}")
def update_registry_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], registry_id: str, payload: RegistryUpdateSchema, db: Session = Depends(get_db)):
    return admin_update_registry(current_user, registry_id, payload, db)

@router.post("/refresh/{registry_id}")
def refresh_registry_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], registry_id: str, db: Session = Depends(get_db)):
    return admin_refresh_registry(current_user, registry_id, db)

@router.get("/{provider}/{region}/all")
def get_all_registries(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, db: Session = Depends(get_db)):
    return admin_get_registries(current_user, provider, region, db)

@router.get("/{provider}/{region}/{user_id}")
def get_user_registries(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, user_id: str, db: Session = Depends(get_db)):
    return admin_get_user_registries(current_user, provider, region, user_id, db)
