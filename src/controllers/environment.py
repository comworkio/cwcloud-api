import json

from typing import Literal

from fastapi.responses import JSONResponse

from entities.Environment import Environment
from entities.User import User
from utils.common import is_numeric
from utils.encoder import AlchemyEncoder
from utils.flag import is_flag_disabled
from utils.observability.cid import get_current_cid

def get_environment(current_user, environment_id, db):
    if not is_numeric(environment_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid environment id',
            'i18n_code': 'invalid_payment_method_id',
            'cid': get_current_cid()
        }, status_code = 400)

    env = Environment.getAvailableEnvironmentById(environment_id, db)

    if not env:
        JSONResponse(content = {
            'status': 'ko',
            'error' : 'environment not found',
            'i18n_code': 'environment_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    user = User.getUserById(current_user.id, db)
    if is_flag_disabled(user.enabled_features, "daasapi") and env.type == "vm" and not user.is_admin:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'permission denied',
            'i18n_code': 'not_daasapi',
            'cid': get_current_cid()
        }, status_code = 403)
    elif is_flag_disabled(user.enabled_features, "k8sapi") and env.type == "k8s" and not user.is_admin:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'permission denied',
            'i18n_code': 'not_k8sapi',
            'cid': get_current_cid()
        }, status_code = 403)

    env_json = json.loads(json.dumps(env, cls = AlchemyEncoder))

    return JSONResponse(content = env_json, status_code = 200)

def get_environments(type: Literal["vm", "k8s", "all"], db):
    if type == "all":
        envs = Environment.getAllAvailableEnvironments(db)
    else:
        envs = Environment.getAllAvailableEnvironmentsByType(type, db)

    envs_json = json.loads(json.dumps(envs, cls = AlchemyEncoder))
    return JSONResponse(content = envs_json, status_code = 200)
