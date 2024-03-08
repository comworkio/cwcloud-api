from typing import Annotated, Union
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema, UserAdminUpdateSchema, UserAdminUpdateRoleSchema, UserAdminAddSchema
from controllers.admin.admin_user import admin_add_user, admin_delete_user_2fa, admin_get_billable_users, admin_get_user, admin_get_users, admin_remove_user, admin_update_user, admin_update_user_confirmation, admin_update_user_role, admin_get_autopayment_users

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-user"

@router.get("/all")
def get_all_users(current_user: Annotated[UserSchema, Depends(admin_required)], no_per_page: Union[str, None] = None, page: Union[str, None] = None, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return admin_get_users(current_user, no_per_page, page, db)

@router.post("")
def add_user(current_user: Annotated[UserSchema, Depends(admin_required)], payload: UserAdminAddSchema , db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        return admin_add_user(current_user, payload, db)

@router.get("/{user_id}")
def get_user_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return admin_get_user(current_user, user_id, db)

@router.put("/{user_id}")
def update_user_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, payload: UserAdminUpdateSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-put".format(_span_prefix)):
        return admin_update_user(current_user, user_id, payload, db)

@router.delete("/{user_id}")
def delete_user_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        return admin_remove_user(current_user, user_id, db)

@router.patch("/confirm/{user_id}")
def update_user_confirmation_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-confirm".format(_span_prefix)):
        return admin_update_user_confirmation(current_user, user_id, db)

@router.patch("/confirm/admin/{user_id}")
def update_user_role_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, payload: UserAdminUpdateRoleSchema , db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-grant-adm".format(_span_prefix)):
        return admin_update_user_role(current_user, user_id, payload, db)

@router.delete("/2fa/{user_id}")
def delete_user_2fa_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete-2fa".format(_span_prefix)):
        return admin_delete_user_2fa(current_user, user_id, db)

@router.get("/auto-payment/all")
def get_all_autopayment_users(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-autopayers".format(_span_prefix)):
        return admin_get_autopayment_users(current_user, db)

@router.get("/billable/all")
def get_all_billable_users(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-billable".format(_span_prefix)):
        return admin_get_billable_users(current_user, db)
