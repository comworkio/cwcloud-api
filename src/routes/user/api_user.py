from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated

from schemas.User import UserRegisterSchema, UserUpdateSchema, UserSchema, UserUpdatePasswordSchema, UserLoginSchema, UserPaymentSchema, UserPaymentMethodSchema
from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from controllers.user import add_payment_method, confirm_user_account, confirmation_email, create_user_account, forget_password_email, get_current_user_data, get_payment_methods, get_user_cloud_resources, remove_payment_method, update_payment_method, update_user_informations, update_user_password, user_reset_password, verify_user_token, get_user_cloud_statistics, update_user_autopayment

router = APIRouter()

@router.post("")
def create_user(payload: UserRegisterSchema, db: Session = Depends(get_db)):
    return create_user_account(payload, db)

@router.put("")
def update_user(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: UserRegisterSchema, db: Session = Depends(get_db)):
    return update_user_informations(current_user, payload, db)

@router.get("")
def get_user(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    return get_current_user_data(current_user, db)

@router.get("/statistics")
def get_user_statistics(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    return get_user_cloud_statistics(current_user, db)

@router.get("/resources")
def get_user_resources(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    return get_user_cloud_resources(current_user, db)

@router.patch("/password")
def update_password(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: UserUpdatePasswordSchema, db: Session = Depends(get_db)):
    return update_user_password(current_user, payload, db)

@router.post("/forget-password")
def forget_password(payload: UserUpdateSchema, db: Session = Depends(get_db)):
    return forget_password_email(payload, db)

@router.post("/reset-password")
def reset_password(payload: UserLoginSchema, db: Session = Depends(get_db)):
    return user_reset_password(payload, db)

@router.get("/verify/{token}")
def verify_token(token: str, db: Session = Depends(get_db)):
    return verify_user_token(token, db)

@router.patch("/payment/auto-payment")
def update_autopayment(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: UserPaymentSchema, db: Session = Depends(get_db)):
    return update_user_autopayment(current_user, payload, db)

@router.post("/confirm/{token}")
def confirm_account(token: str, db: Session = Depends(get_db)):
    return confirm_user_account(token, db)

@router.post("/confirmation-mail")
def confirm_email(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: UserUpdateSchema, db: Session = Depends(get_db)):
    return confirmation_email(payload, db)

@router.get("/payment-method")
def get_methods(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    return get_payment_methods(current_user, db)

@router.post("/payment-method")
def add_methods(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: UserPaymentMethodSchema, db: Session = Depends(get_db)):
    return add_payment_method(current_user, payload, db)

@router.delete("/payment-method/{payment_method_id}")
def delete_payment_method(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payment_method_id: str, db: Session = Depends(get_db)):
    return remove_payment_method(current_user, payment_method_id, db)

@router.patch("/payment-method/{payment_method_id}")
def update_payment(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payment_method_id: str, db: Session = Depends(get_db)):
    return update_payment_method(current_user, payment_method_id, db)
