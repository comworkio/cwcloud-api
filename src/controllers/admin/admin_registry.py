import json

from pulumi import automation as auto
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from urllib.error import HTTPError

from entities.Registry import Registry
from entities.User import User

from utils.registry import create_registry, delete_registry, refresh_registry, register_registry, update_credentials
from utils.common import is_empty, is_not_empty, is_numeric, is_true
from utils.instance import check_instance_name_validity
from utils.dynamic_name import generate_hashed_name
from utils.encoder import AlchemyEncoder
from utils.provider import exist_provider, get_provider_infos
from utils.observability.cid import get_current_cid

def admin_add_registry(current_user, provider, region, payload, db, bt: BackgroundTasks):
    name = payload.name
    type = payload.type
    email = payload.email

    try:
        if not exist_provider(provider):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'provider does not exist', 
                'i18n_code': 'provider_not_exist',
                'cid': get_current_cid()
            }, status_code = 404)

        if is_empty(name):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'please provide registry name', 
                'i18n_code': 'provide_registry_name',
                'cid': get_current_cid()
            }, status_code = 400)

        if is_empty(email):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'please provide an email', 
                'i18n_code': 'provide_email',
                'cid': get_current_cid()
            }, status_code = 400)

        if len(get_provider_infos(provider, "registry_types"))>0:
            if is_empty(type) :
                type = get_provider_infos(provider, "registry_types")[0]
            else:
                possible_types = get_provider_infos(provider, "registry_types")
                if type not in possible_types:
                    return JSONResponse(content = {
                        'status': 'ko',
                        'error': 'registry type does not exist', 
                        'i18n_code': 'registry_type_not_exist',
                        'cid': get_current_cid()
                    }, status_code = 400)

        possible_regions = get_provider_infos(provider, "registry_available_regions")
        if region not in possible_regions:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'region does not exist', 
                'i18n_code': 'region_not_exist',
                'cid': get_current_cid()
            }, status_code = 400)

        exist_user = User.getUserByEmail(email, db)
        if not exist_user:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'user not found', 
                'i18n_code': 'user_not_found',
                'cid': get_current_cid()
            }, status_code = 404)
        userid = exist_user.id

        check_instance_name_validity(name)
        hash, hashed_registry_name = generate_hashed_name(name)
        new_registry = register_registry(hash, provider, region, userid, name, type, db)

        bt.add_task(create_registry,
            provider,
            exist_user.email,
            new_registry.id,
            hashed_registry_name,
            region,
            type,
            db
        )

        new_registry_json = json.loads(json.dumps(new_registry, cls = AlchemyEncoder))
        return JSONResponse(content = new_registry_json, status_code = 200)
    except auto.StackAlreadyExistsError:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'stack already exists', 
            'i18n_code': 'stack_exists',
            'cid': get_current_cid()
        }, status_code = 409)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)
    except Exception as exn:
        error = {"error": f"{exn}"}
        return JSONResponse(content = error, status_code = 500)

def admin_get_registry(current_user, registryId, db):
    if not is_numeric(registryId):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid registry id',
            'cid': get_current_cid()
        }, status_code = 400)

    user_Registry = Registry.findById(registryId, db)
    if not user_Registry:
        return JSONResponse(content = { 
            'status': 'ko',   
            'error': 'registry not found', 
            'i18n_code': 'registry_not_found',
            'cid': get_current_cid()
        }, status_code = 404)

    dumpedRegistry = json.loads(json.dumps(user_Registry, cls = AlchemyEncoder))
    dumpedUser = json.loads(json.dumps(user_Registry.user, cls = AlchemyEncoder))
    registryJson = {**dumpedRegistry, "user": {**dumpedUser}}
    return JSONResponse(content = registryJson, status_code = 200)

def admin_remove_registry(current_user, registry_id, db, bt: BackgroundTasks):
    if not is_numeric(registry_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid registry id',
            'cid': get_current_cid()
        }, status_code = 400)

    user_registry = Registry.findById(registry_id, db)
    if not user_registry:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'registry not found', 
            'i18n_code': 'registry_not_found',
            'cid': get_current_cid()
        }, status_code = 404)

    user_id = user_registry.user_id
    user = User.getUserById(user_id, db) if is_not_empty(user_id) else None
    user_email = user.email if user is not None else None

    if is_empty(user_email):
        Registry.updateStatus(user_registry.id, 'deleted', db)
        return JSONResponse(content = {
            'status': 'ko',
            'error': "user doesn't exists anymore", 
            'i18n_code': 'user_not_found',
            'cid': get_current_cid()
        }, error = 404)

    try:
        bt.add_task(delete_registry, user_registry.provider, user_registry, user_email)
        Registry.updateStatus(user_registry.id, "deleted", db)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'registry successfully deleted', 
            'i18n_code': 'registry_deleted'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)

def admin_update_registry(current_user, registryId, payload, db):
    if not is_numeric(registryId):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid registry id',
            'i18n_code': 'invalid_registry_id',
            'cid': get_current_cid()
        }, status_code = 400)

    user_registry = Registry.findById(registryId, db)
    if not user_registry:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'registry not found', 
            'i18n_code': 'registry_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    try:
        if is_true(payload.update_creds):
            update_credentials(user_registry.provider, user_registry, user_registry.user.email, db)

        if is_not_empty(payload.email):
            user = User.getUserByEmail(payload.email, db)
            if not user:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'user not found', 
                    'i18n_code': 'user_not_found',
                    'cid': get_current_cid()
                }, status_code = 404)
            Registry.patch(registryId, {"user_id": user.id}, db)

        return JSONResponse(content = {
            'status': 'ok',
            'message': 'registry successfully updated', 
            'i18n_code': 'registry_deleted'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)

def admin_refresh_registry(current_user, registry_id, db):
    if not is_numeric(registry_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid registry id',
            'cid': get_current_cid()
        }, status_code = 400)

    user_registry = Registry.findById(registry_id, db)
    if not user_registry:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Registry not found', 
            'i18n_code': 'registry_not_found',
            'cid': get_current_cid()
        }, status_code = 404)

    hashed_registry_name = f"{user_registry.name}-{user_registry.hash}"
    refresh_registry(current_user.email, user_registry.provider, user_registry.id, hashed_registry_name, db)
    return JSONResponse(content = {'message': 'done','status': 'ok'}, status_code = 200)

def admin_get_registries(current_user, provider, region, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist', 
            'i18n_code': 'provider_not_exist',
            'cid': get_current_cid()
        }, status_code = 404)

    userRegionRegistries = Registry.getAllRegistriesByRegion(provider, region, db)
    userRegionRegistriesJson = json.loads(json.dumps(userRegionRegistries, cls = AlchemyEncoder))
    return JSONResponse(content = userRegionRegistriesJson, status_code = 200)

def admin_get_user_registries(current_user, provider, region, user_id, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist' , 
            'i18n_code': 'provider_not_exist',
            'cid': get_current_cid()
        }, status_code = 404)

    userRegionRegistries = Registry.getAllUserRegistriesByRegion(provider, region, user_id, db)
    userRegionRegistriesJson = json.loads(json.dumps(userRegionRegistries, cls = AlchemyEncoder))
    return JSONResponse(content = userRegionRegistriesJson, status_code = 200)
