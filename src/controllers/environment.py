import json
from typing import Literal

from fastapi.responses import JSONResponse

from entities.Environment import Environment
from entities.User import User
from utils.common import is_not_numeric, is_numeric
from utils.encoder import AlchemyEncoder
from utils.flag import is_flag_disabled
from utils.logger import log_msg
from utils.observability.cid import get_current_cid

def get_environment(current_user, environment_id, db):
    if not is_numeric(environment_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid environment id',
            'i18n_code': 'invalid_numeric_id',
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

def get_environments(type: Literal["vm", "k8s", "all"], start_index, max_results, db):
    if is_not_numeric(start_index) or is_not_numeric(max_results):
        log_msg("DEBUG", f"[get_environments][1] type = {type}, start_index = {start_index}, max_results = {max_results}")
        envs = Environment.getAllAvailableEnvironments(db) if type == "all" else Environment.getAllAvailableEnvironmentsByType(type, db)
    elif type == "all":
        log_msg("DEBUG", f"[get_environments][2] type = {type}, start_index = {start_index}, max_results = {max_results}")
        envs = Environment.getAllAvailableEnvironmentsPaged(start_index, max_results, db)
    else:
        log_msg("DEBUG", f"[get_environments][3] type = {type}, start_index = {start_index}, max_results = {max_results}")
        envs = Environment.getAllAvailableEnvironmentsByTypePaged(type, start_index, max_results, db)

    envs_json = json.loads(json.dumps(envs, cls = AlchemyEncoder))
    return JSONResponse(content = envs_json, status_code = 200)
