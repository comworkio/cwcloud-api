from middleware.emailapi_guard import emailapi_required
from utils.common import is_empty
from utils.logger import log_msg
from utils.mail import EMAIL_ADAPTER
from fastapi import Depends, APIRouter
from typing import Annotated
from schemas.User import UserSchema
from schemas.Email import EmailSchema
from middleware.auth_guard import get_current_active_user
from fastapi.responses import JSONResponse


router = APIRouter()

@router.post("")
def send_email(current_user: Annotated[UserSchema, Depends(get_current_active_user)], email_api: Annotated[str, Depends(emailapi_required)], payload: EmailSchema):
    if EMAIL_ADAPTER().is_disabled():
        return JSONResponse(content = {
            "status": "disabled",
            "i18n_code": "disabled_email_service"
        }, status_code = 405)

    if is_empty(payload.from_):
        payload.from_ = current_user.email

    email = payload.dict(by_alias = True)
    log_msg("DEBUG", "[api_email] email = {}".format(email))

    return EMAIL_ADAPTER().send(email)
