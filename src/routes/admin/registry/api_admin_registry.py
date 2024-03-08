
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, BackgroundTasks

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from schemas.Registry import RegistrySchema, RegistryUpdateSchema
from controllers.admin.admin_registry import admin_add_registry, admin_get_registries, admin_get_registry, admin_get_user_registries, admin_refresh_registry, admin_remove_registry, admin_update_registry

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-registry"

@router.post("/{provider}/{region}/provision")
def add_registry(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, payload: RegistrySchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        return admin_add_registry(current_user, provider, region, payload, db, bt)

@router.get("/{registry_id}")
def get_registry_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], registry_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return admin_get_registry(current_user, registry_id, db)

@router.delete("/{registry_id}")
def delete_registry_by_id(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(admin_required)], registry_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        return admin_remove_registry(current_user, registry_id, db, bt)

@router.patch("/{registry_id}")
def update_registry_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], registry_id: str, payload: RegistryUpdateSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-patch".format(_span_prefix)):
        return admin_update_registry(current_user, registry_id, payload, db)

@router.post("/refresh/{registry_id}")
def refresh_registry_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], registry_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-refresh".format(_span_prefix)):
        return admin_refresh_registry(current_user, registry_id, db)

@router.get("/{provider}/{region}/all")
def get_all_registries(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return admin_get_registries(current_user, provider, region, db)

@router.get("/{provider}/{region}/{user_id}")
def get_user_registries(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-byuser".format(_span_prefix)):
        return admin_get_user_registries(current_user, provider, region, user_id, db)
