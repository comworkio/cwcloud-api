import json

from fastapi.responses import JSONResponse

from entities.Environment import Environment
from utils.common import is_numeric
from utils.encoder import AlchemyEncoder

def get_environment(current_user, environmentId, db):
    if not is_numeric(environmentId):
        return JSONResponse(content = {"error": "Invalid environment id", "i18n_code": "400"}, status_code = 400)
    env = Environment.getAvailableEnvironmentById(environmentId, db)
    if not env:
        JSONResponse(content = {"message" : "environment not found", "i18n_code": "804"}, status_code = 404)
    envJson = json.loads(json.dumps(env, cls = AlchemyEncoder))
    return JSONResponse(content = envJson, status_code = 200)

def get_environments(current_user, db):
    envs = Environment.getAllAvailableEnvironments(db)
    envsJson = json.loads(json.dumps(envs, cls = AlchemyEncoder))
    return JSONResponse(content = envsJson, status_code = 200)
