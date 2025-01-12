import json

from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from entities.iot.ObjectType import ObjectType

from utils.common import is_true
from utils.encoder import AlchemyEncoder
from utils.file import get_b64_content
from utils.iot.object_type import object_type_user_content_check
from utils.observability.cid import get_current_cid

def get_object_types(current_user, db):
    object_types = ObjectType.getUserObjectTypes(current_user.id, db)
    return object_types

def get_object_type(current_user, object_type_id, db):
    object_type = ObjectType.findUserObjectTypeById(current_user.id, object_type_id, db)
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
        object_type_user_content_check(current_user, payload, db)

        new_object_type = ObjectType(**payload.dict())
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
    object_type = ObjectType.findUserObjectTypeById(current_user.id, object_type_id, db)
    if not object_type:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Object type not found',
            'i18n_code': 'object_type_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    object_type_user_content_check(current_user, payload, db)

    current_date = datetime.now().date().strftime('%Y-%m-%d')
    ObjectType.updateObjectType(object_type_id, payload, current_date, db)

    return JSONResponse(content = {
        'status': 'ok',
        'message': 'Object type successfully updated',
        'i18n_code': 'object_type_updated'
    }, status_code = 200)

def delete_object_type(current_user, object_type_id, db):
    object_type = ObjectType.findUserObjectTypeById(current_user.id, object_type_id, db)
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

def import_new_object_type(current_user, object_type_file, db):
    object_type_json = object_type_file.file.read()
    object_type_dict = json.loads(object_type_json)
    current_date = datetime.now().date().strftime('%Y-%m-%d')

    new_object_type = ObjectType()
    new_object_type.user_id = current_user.id
    new_object_type.content = object_type_dict["content"]
    new_object_type.created_at = current_date
    new_object_type.updated_at = current_date
    db.add(new_object_type)
    db.commit()

    return JSONResponse(content = {
        'status': 'ok',
        'message': 'Object type successfully imported',
        'id': str(new_object_type.id),
        'i18n_code': 'object_type_imported'
    }, status_code = 201)


def export_object_type(current_user, object_type_id, db):
    object_type = ObjectType.findUserObjectTypeById(current_user.id, object_type_id, db)

    if is_true(current_user.is_admin):
        object_type = ObjectType.findById(object_type_id, db)

    if not object_type:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Object type not found',
            'i18n_code': 'object_type_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    object_type_dict = json.loads(json.dumps(object_type, cls = AlchemyEncoder))
    object_type_json = json.dumps(object_type_dict, indent=4)
    file_name = f"object_type_{object_type_id}.json"
    with open(file_name, "w") as outfile:
        outfile.write(object_type_json)

    encoded_string = get_b64_content(file_name, True)

    return JSONResponse(content = {
        "file_name": file_name,
        "blob": str(encoded_string)
    }, status_code = 200)
