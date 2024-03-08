from typing import Annotated
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from schemas.Email import EmailAdminSchema

from utils.common import is_empty, is_true
from utils.logger import log_msg
from utils.observability.otel import get_otel_tracer
from utils.mail import EMAIL_ADAPTER, send_templated_email

router = APIRouter()

_span_prefix = "adm-email"

@router.post("")
def send_email(current_user: Annotated[UserSchema, Depends(admin_required)], payload: EmailAdminSchema):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
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
