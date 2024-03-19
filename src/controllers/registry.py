import json

from urllib.error import HTTPError
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse

from entities.Registry import Registry

from utils.common import is_numeric
from utils.encoder import AlchemyEncoder
from utils.provider import exist_provider
from utils.registry import delete_registry, update_credentials
from utils.common import is_empty, is_numeric
from utils.observability.cid import get_current_cid

def get_registry(current_user, provider, region, registryId, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist', 
            'i18n_code': '504',
            'cid': get_current_cid()
        }, status_code = 404)
    if not is_numeric(registryId):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid registry id', 
            'i18n_code': '400',
            'cid': get_current_cid()
        }, status_code = 400)

    userRegistry = Registry.findUserRegistry(provider, current_user.id, registryId, region, db)
    if not userRegistry:
        from entities.Access import Access
        access = Access.getUserAccessToObject(current_user.id, "registry", registryId, db)
        if not access:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'registry not found', 
                'i18n_code': '904',
                'cid': get_current_cid()
            }, status_code = 404)
        userRegistry = Registry.findRegistry(provider, region, registryId)
    dumpedRegistry = json.loads(json.dumps(userRegistry, cls = AlchemyEncoder))
    return JSONResponse(content = dumpedRegistry, status_code = 200)

def remove_registry(current_user, provider, region, registryId, db, bt: BackgroundTasks):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist', 
            'i18n_code': '504',
            'cid': get_current_cid()
        }, status_code = 404)
    if not is_numeric(registryId):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid registry id', 
            'i18n_code': '400',
            'cid': get_current_cid()
        }, status_code = 400)

    user_registry = Registry.findUserRegistry(provider, current_user.id, registryId, region, db)
    if not user_registry:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'registry not found', 
            'i18n_code': '904',
            'cid': get_current_cid()
        }, status_code = 404)

    user_email = user_registry.user.email if user_registry.user is not None else None
    if is_empty(user_email):
        return JSONResponse(content = {
            'status': 'ko',
            'error': "user doesn't exists anymore", 
            'i18n_code': 'user_not_found',
            'cid': get_current_cid()
        }, status_code = 404)

    try:
        bt.add_task(delete_registry, user_registry.provider, user_registry, user_email)
        Registry.updateStatus(user_registry.id, "deleted", db)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'registry successfully deleted', 
            'i18n_code': '902'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)

def update_registry(current_user, provider, region, registryId, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist', 
            'i18n_code': '504',
            'cid': get_current_cid()
        }, status_code = 404)
    if not is_numeric(registryId):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid registry id', 
            'i18n_code': '400',
            'cid': get_current_cid()
        }, status_code = 400)

    user_registry = Registry.findUserRegistry(provider, current_user.id, registryId, region, db)
    if not user_registry:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'registry not found', 
            'i18n_code': '904',
            'cid': get_current_cid()
        }, status_code = 404)
    try:
        update_credentials(user_registry.provider, user_registry, user_registry.user.email, db)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'registry successfully updated', 
            'i18n_code': '902'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)

def get_registries(current_user, provider, region, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist', 
            'i18n_code': '504',
            'cid': get_current_cid()
        }, status_code = 404)

    userRegionRegistries = Registry.getAllUserRegistriesByRegion(provider, region, current_user.id, db)
    from entities.Access import Access
    other_registries_access = Access.getUserAccessesByType(current_user.id, "registry", db)
    other_registries_ids = [access.object_id for access in other_registries_access]
    other_registries = Registry.findRegistriesByRegion(other_registries_ids, provider, region, db)
    userRegionRegistries.extend(other_registries)
    userRegionRegistriesJson = json.loads(json.dumps(userRegionRegistries, cls = AlchemyEncoder))
    return JSONResponse(content = userRegionRegistriesJson, status_code = 200)
