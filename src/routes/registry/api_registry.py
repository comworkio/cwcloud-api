from fastapi import Depends, APIRouter, BackgroundTasks
from typing import Annotated
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from controllers.registry import get_registries, get_registry, remove_registry, update_registry


router = APIRouter()

@router.get("/{provider}/{region}")
def get_all_registries(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, db: Session = Depends(get_db)):
    return get_registries(current_user, provider, region, db)

@router.get("/{provider}/{region}/{registryId}")
def get_registry_info(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, registryId: str, db: Session = Depends(get_db)):
    return get_registry(current_user, provider, region, registryId, db)

@router.delete("/{provider}/{region}/{registryId}")
def delete_registry(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, registryId: str, db: Session = Depends(get_db)):
    return remove_registry(current_user, provider, region, registryId, db, bt)

@router.patch("/{provider}/{region}/{registryId}")
def patch_registry_data(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, registryId: str, db: Session = Depends(get_db)):
    return update_registry(current_user, provider, region, registryId, db)
