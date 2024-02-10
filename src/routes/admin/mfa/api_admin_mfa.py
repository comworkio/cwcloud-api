from urllib.error import HTTPError
import json
from utils.encoder import AlchemyEncoder
from entities.Mfa import Mfa
from fastapi import Depends, APIRouter, status
from database.postgres_db import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from schemas.User import UserSchema
from middleware.auth_guard import admin_required
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/user/{user_id}")
def get_user_mfa_methods(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    try:
        mfaMethods = Mfa.getUserMfaMethods(user_id, db)
        mfaMethodsJson = json.loads(json.dumps(mfaMethods, cls = AlchemyEncoder))
        return JSONResponse(content = {"methods": mfaMethodsJson}, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

@router.delete("/user/{user_id}")
def delete_user_method(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
        Mfa.deleteUserMethods(user_id, db)
        return JSONResponse(content = {"message": "2fa successfully deleted"}, status_code = 200)

@router.delete("/{method_id}")
def delete_method(current_user: Annotated[UserSchema, Depends(admin_required)], method_id: str, db: Session = Depends(get_db)):
    try:
        method = Mfa.findOne(method_id, db)
        if not method:
            return JSONResponse(content = {"message": "2fa method not found"}, status_code = 404)

        Mfa.deleteOne(method.id, db)
        return JSONResponse(content = {"message": "successfully deleted mfa method"}, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)