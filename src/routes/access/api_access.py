import json

from urllib.error import HTTPError
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from database.postgres_db import get_db
from schemas.User import UserSchema
from schemas.Access import AccessSchema
from middleware.auth_guard import get_current_active_user

from utils.observability.counter import create_counter, increment_counter
from utils.observability.cid import get_current_cid
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.enums import Method
from utils.encoder import AlchemyEncoder
from utils.gitlab import attach_default_gitlab_project_to_user, detach_user_gitlab_project

router = APIRouter()

_span_prefix = "access"
_counter = create_counter("access_api", "Access API counter")

@router.get("")
def get_access(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        try:
            from entities.Access import Access
            access = Access.getOwnerAccesses(current_user.id, db)
            accessJson = json.loads(json.dumps(access, cls = AlchemyEncoder))
            return JSONResponse(content = {
                'status': 'ok',
                'access': accessJson
            }, status_code = 200)
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg,
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)

@router.post("")
def create_access(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: AccessSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        email = payload.email
        object_id = payload.object_id
        object_type = payload.object_type

        if object_type not in ["project", "instance", "bucket", "registry"]:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'invalid object type',
                'cid': get_current_cid()
            }, status_code = 400)

        from entities.User import User
        user = User.getUserByEmail(email, db)
        if not user:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'user not found',
                'i18n_code': "user_not_found",
                'cid': get_current_cid()
            }, status_code = 409)

        from entities.Access import Access
        access_object = Access.getUserAccessToObject(user.id, object_type, object_id, db)
        if access_object:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'access already exists',
                'i18n_code': 'user_not_found',
                'cid': get_current_cid()
            }, status_code = 400)

        if object_type == "project":
            from entities.Project import Project
            project = Project.getById(object_id, db)
            attach_default_gitlab_project_to_user(project.id, user.email)

        payload_dict = payload.dict()
        payload_dict.pop("email")
        new_access = Access(**payload_dict)
        new_access.user_id = user.id
        new_access.owner_id = current_user.id
        new_access.save(db)
        accessJson = json.loads(json.dumps(new_access, cls = AlchemyEncoder))
        accessJson["id"] = new_access.id
        return JSONResponse(content = {
            'status': 'ok',
            'access': accessJson
        }, status_code = 201)

@router.delete("/{access_id}")
def delete_access(current_user: Annotated[UserSchema, Depends(get_current_active_user)], access_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        try:
            from entities.Access import Access
            access = Access.findById(access_id, db)
            if not access:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'access not found',
                    'cid': get_current_cid()
                }, status_code = 404)

            if access.object_type == "project":
                from entities.User import User
                user = User.getUserById(access.user_id, db)
                detach_user_gitlab_project(access.object_id, user.email)

            Access.deleteOne(access_id, db)

            return JSONResponse(content = {
                'status': 'ok',
                'message': 'successfully delete access'
            }, status_code = 200)
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg,
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)
