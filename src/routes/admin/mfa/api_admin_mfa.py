import json

from urllib.error import HTTPError
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from entities.Mfa import Mfa

from utils.encoder import AlchemyEncoder
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-mfa"

@router.get("/user/{user_id}")
def get_user_mfa_methods(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        try:
            mfaMethods = Mfa.getUserMfaMethods(user_id, db)
            mfaMethodsJson = json.loads(json.dumps(mfaMethods, cls = AlchemyEncoder))
            return JSONResponse(content = {"methods": mfaMethodsJson}, status_code = 200)
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

@router.delete("/user/{user_id}")
def delete_user_method(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete-byuser".format(_span_prefix)):
        Mfa.deleteUserMethods(user_id, db)
        return JSONResponse(content = {"message": "2fa successfully deleted"}, status_code = 200)

@router.delete("/{method_id}")
def delete_method(current_user: Annotated[UserSchema, Depends(admin_required)], method_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        try:
            method = Mfa.findOne(method_id, db)
            if not method:
                return JSONResponse(content = {"message": "2fa method not found"}, status_code = 404)

            Mfa.deleteOne(method.id, db)
            return JSONResponse(content = {"message": "successfully deleted mfa method"}, status_code = 200)
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
