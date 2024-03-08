import json
import os

from datetime import datetime
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from adapters.AdapterConfig import get_adapter
from schemas.User import UserLoginSchema
from database.postgres_db import get_db
from utils.jwt import jwt_encode

from utils.logger import log_msg
from utils.common import verify_password
from utils.flag import is_flag_enabled
from utils.encoder import AlchemyEncoder
from utils.observability.otel import get_otel_tracer

router = APIRouter()
CACHE_ADAPTER = get_adapter('cache')

_span_prefix = "login"

@router.post("/login")
def login_user(payload: UserLoginSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        from entities.User import User
        email = payload.email
        password = payload.password

        if not payload or not email or not password:
            return JSONResponse(content = {"error": "Missing informations for login", "i18n_code": "1004"}, status_code = 403)

        user = User.getUserByEmail(email, db)
        if not user:
            log_msg("WARN", "User {} try to authenticate but it not exists".format(email))
            return JSONResponse(content = {"error": "Authentification failed", "i18n_code": "1002"}, status_code = 403)

        from entities.Mfa import Mfa
        mfaMethods = Mfa.getUserMfaMethods(user.id, db)
        if verify_password(password, user.password):
            token = jwt_encode({
                "id": user.id,
                "email": user.email,
                "confirmed": user.confirmed,
                "is_admin": user.is_admin,
                "emailapi": is_flag_enabled(user.enabled_features, 'emailapi'),
                "cwaiapi": is_flag_enabled(user.enabled_features, 'cwaiapi'),
                "verified": "true" if len(mfaMethods) == 0 else "false",
                "time": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            })
            CACHE_ADAPTER().delete(user.email)
            CACHE_ADAPTER().put(user.email, token, int(os.getenv("TOKEN_EXPIRATION_TIME")))
            from entities.Mfa import Mfa
            mfaMethods = Mfa.getUserMfaMethods(user.id, db)
            mfaMethodsJson = json.loads(json.dumps(mfaMethods, cls = AlchemyEncoder))
            log_msg("INFO", "User {} successfully authenticated".format(user.email))
            return JSONResponse(content = {"token": token, "confirmed": user.confirmed, "methods": mfaMethodsJson }, status_code = 200)

        log_msg("WARN", "User {} fails to authenticate".format(user.email))
        return JSONResponse(content = {"error": "Authentification failed", "i18n_code": "1002"}, status_code = 403)
