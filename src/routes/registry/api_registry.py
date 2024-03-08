from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, BackgroundTasks

from schemas.User import UserSchema
from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from controllers.registry import get_registries, get_registry, remove_registry, update_registry

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "registry"

@router.get("/{provider}/{region}")
def get_all_registries(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return get_registries(current_user, provider, region, db)

@router.get("/{provider}/{region}/{registryId}")
def get_registry_info(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, registryId: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return get_registry(current_user, provider, region, registryId, db)

@router.delete("/{provider}/{region}/{registryId}")
def delete_registry(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, registryId: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        return remove_registry(current_user, provider, region, registryId, db, bt)

@router.patch("/{provider}/{region}/{registryId}")
def patch_registry_data(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, registryId: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-patch".format(_span_prefix)):
        return update_registry(current_user, provider, region, registryId, db)
