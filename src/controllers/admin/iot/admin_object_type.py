from datetime import datetime
from entities.iot.ObjectType import ObjectType
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from utils.common import is_empty
from utils.iot.object_type import object_type_admin_content_check
from utils.observability.cid import get_current_cid

def get_object_types(current_user, db):
    object_types = ObjectType.getAllObjectTypes(db)
    return object_types

def get_object_type(current_user, object_type_id, db):
    object_type = ObjectType.findById(object_type_id)
    if not object_type:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Object type not found',
            'i18n_code': 'object_type_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    return object_type

def add_object_type(current_user, payload, db):
    try:
        object_type_admin_content_check(payload, db)
        new_object_type = ObjectType(**payload.dict())
        if is_empty(new_object_type.user_id):
            new_object_type.user_id = current_user.id
        current_date = datetime.now().date().strftime('%Y-%m-%d')
        new_object_type.created_at = current_date
        new_object_type.updated_at = current_date
        db.add(new_object_type)
        db.commit()
        db.refresh(new_object_type)

        return JSONResponse(content = {
            'status': 'ok',
            'message': 'Object type successfully created',
            'id': str(new_object_type.id),
            'i18n_code': 'object_type_created'
        }, status_code = 201)

    except HTTPException as e:
        return JSONResponse(content = {
            'status': 'ko',
            'message': e.detail,
            'i18n_code': e.detail,
            'cid': get_current_cid()
        }, status_code = e.status_code)

def update_object_type(current_user, object_type_id, payload, db):
    object_type = ObjectType.findById(object_type_id)
    if not object_type:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Object type not found',
            'i18n_code': 'object_type_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    object_type_admin_content_check(payload, db)

    current_date = datetime.now().date().strftime('%Y-%m-%d')
    ObjectType.updateObjectType(object_type_id, payload, current_date, db)

    return JSONResponse(content = {
        'status': 'ok',
        'message': 'Object type successfully updated',
        'id': str(object_type_id),
        'i18n_code': 'object_type_updated'
    }, status_code = 200)

def delete_object_type(current_user, object_type_id, db):
    object_type = ObjectType.findById(object_type_id)
    if not object_type:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Object type not found',
            'i18n_code': 'object_type_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    ObjectType.deleteObjectType(object_type_id, db)

    return JSONResponse(content = {
        'status': 'ok',
        'message': 'Object type successfully deleted',
        'i18n_code': 'object_type_deleted'
    }, status_code = 200)
