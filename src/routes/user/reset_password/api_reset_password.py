from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from typing import Annotated
from sqlalchemy.orm import Session

from schemas.User import UserLoginSchema, UserSchema
from database.postgres_db import get_db
from middleware.auth_guard import admin_required

from utils.common import generate_hash_password, is_empty, is_false
from utils.security import check_password
from utils.bytes_generator import generate_random_bytes
from utils.mail import send_email
from utils.observability.cid import get_current_cid
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "reset-password"
_counter = create_counter("reset_password_api", "Reset password API counter")

@router.patch("/user/reset-password")
def reset_password(current_user: Annotated[UserSchema, Depends(admin_required)], payload: UserLoginSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.PATCH)):
        increment_counter(_counter, Method.PATCH)
        user_email = payload.email
        user_new_password = payload.password

        from entities.User import User
        target_user = User.getUserByEmail(user_email, db)
        if not target_user:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'User not found',
                'i18n_code': 'user_not_found',
                'cid': get_current_cid()
            }, status_code = 404)

        is_not_set_password = is_empty(user_new_password)
        if is_not_set_password:
            user_new_password = generate_random_bytes(24)
        else:
            check = check_password(user_new_password)
            if is_false(check["status"]):
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'password not valid',
                    'i18n_code': check['i18n_code'],
                    'cid': get_current_cid()
                }, status_code = 400)

        target_user.password = generate_hash_password(user_new_password)
        db.commit()
        subject = "Reset Password"
        message = "Your password changed:<ul>" + \
            "<li> your new password is: " + user_new_password + \
            "</ul>"

        send_email(user_email, message, subject)
        if is_not_set_password:
            return JSONResponse(content = {
                'status': 'ok',
                'message': 'User successfully updated',
                'new_password': user_new_password,
                'i18n_code': 'user_updated'
            }, status_code = 200)

        return JSONResponse(content = {
            'status': 'ok',
            'message': 'User successfully updated',
            'i18n_code': 'user_updated'
        }, status_code = 200)
