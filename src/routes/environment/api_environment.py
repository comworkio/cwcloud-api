from fastapi import Depends, APIRouter
from typing import Annotated, Literal
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from controllers.environment import get_environment, get_environments
from controllers.admin.admin_environment import admin_get_environments, admin_get_environment

router = APIRouter()

@router.get("/all")
def get_all_environments(current_user: Annotated[UserSchema, Depends(get_current_active_user)], type: Literal['vm','k8s'] = "vm", db: Session = Depends(get_db)):
    if current_user.is_admin:
        return admin_get_environments(type, db)
    return get_environments(type, db)

@router.get("/{environment_id}")
def get_environment_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], environment_id: str, db: Session = Depends(get_db)):
    if current_user.is_admin:
        return admin_get_environment(environment_id, db)

    return get_environment(environment_id, db)
