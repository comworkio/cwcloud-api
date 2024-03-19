import json

from typing import Literal

from fastapi.responses import JSONResponse

from entities.Environment import Environment
from utils.common import is_numeric
from utils.encoder import AlchemyEncoder
from utils.observability.cid import get_current_cid

def get_environment(environment_id, db):
    if not is_numeric(environment_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid environment id',
            'i18n_code': '400',
            'cid': get_current_cid()
        }, status_code = 400)

    env = Environment.getAvailableEnvironmentById(environment_id, db)

    if not env:
        JSONResponse(content = {
            'status': 'ko',
            'error' : 'environment not found',
            'i18n_code': '804',
            'cid': get_current_cid()
        }, status_code = 404)

    env_json = json.loads(json.dumps(env, cls = AlchemyEncoder))

    return JSONResponse(content = env_json, status_code = 200)

def get_environments(type: Literal["vm", "k8s", "all"], db):
    if type == "all":
        envs = Environment.getAllAvailableEnvironments(db)
    else:
        envs = Environment.getAllAvailableEnvironmentsByType(type, db)

    envs_json = json.loads(json.dumps(envs, cls = AlchemyEncoder))
    return JSONResponse(content = envs_json, status_code = 200)
