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
from utils.observability.cid import get_current_cid
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "adm-mfa"
_counter = create_counter("adm_mfa_api", "Admin MFA API counter")

@router.get("/user/{user_id}")
def get_user_mfa_methods(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        try:
            mfaMethods = Mfa.getUserMfaMethods(user_id, db)
            mfaMethodsJson = json.loads(json.dumps(mfaMethods, cls = AlchemyEncoder))
            return JSONResponse(content = {"methods": mfaMethodsJson}, status_code = 200)
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg,
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)

@router.delete("/user/{user_id}")
def delete_user_method(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE, Action.BYUSER)):
        increment_counter(_counter, Method.DELETE, Action.BYUSER)
        Mfa.deleteUserMethods(user_id, db)
        return JSONResponse(content = {
            'status': 'ok',
            'message': '2fa successfully deleted'
        }, status_code = 200)

@router.delete("/{method_id}")
def delete_method(current_user: Annotated[UserSchema, Depends(admin_required)], method_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        try:
            method = Mfa.findOne(method_id, db)
            if not method:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': '2fa method not found',
                    'cid': get_current_cid()
                }, status_code = 404)

            Mfa.deleteOne(method.id, db)
            return JSONResponse(content = {
                'status': 'ok',
                'message': 'successfully deleted mfa method'
            }, status_code = 200)
        except HTTPError as e:
            return JSONResponse(content = {
                'error': e.msg,
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)
