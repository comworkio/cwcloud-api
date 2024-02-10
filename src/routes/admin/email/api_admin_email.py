from utils.common import is_empty, is_true
from utils.logger import log_msg
from utils.mail import EMAIL_ADAPTER, send_templated_email
from fastapi import Depends, APIRouter
from typing import Annotated
from schemas.User import UserSchema
from schemas.Email import EmailAdminSchema
from middleware.auth_guard import admin_required
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("")
def send_email(current_user: Annotated[UserSchema, Depends(admin_required)], payload: EmailAdminSchema):
    if EMAIL_ADAPTER().is_disabled():
        return JSONResponse(content = {
            "status": "disabled",
            "i18n_code": "disabled_email_service"
        }, status_code = 405)
    
    if is_empty(payload.from_):
        payload.from_ = current_user.email

    email = payload.dict(by_alias = True)
    log_msg("DEBUG", "[api_admin_email] email = {}".format(email))

    return send_templated_email(email) if "templated" in email and is_true(email['templated']) else EMAIL_ADAPTER().send(email)
