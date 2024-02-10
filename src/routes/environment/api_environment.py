from fastapi import Depends, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from controllers.environment import get_environment, get_environments
from controllers.admin.admin_environment import admin_get_environments, admin_get_environment

router = APIRouter()

@router.get("/all")
def get_all_environments(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if current_user.is_admin:
        return admin_get_environments(current_user, db)
    return get_environments(current_user, db)

@router.get("/{environmentId}")
def get_environment_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], environmentId: str, db: Session = Depends(get_db)):
    if current_user.is_admin:
        return admin_get_environment(current_user, environmentId, db)
    return get_environment(current_user, environmentId, db)
