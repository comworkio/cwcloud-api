import os
import base64
import json

from fastapi.responses import JSONResponse

from entities.Environment import Environment
from utils.gitlab import get_infra_playbook_roles
from utils.list import unmarshall_list_array, marshall_list_string
from utils.common import is_empty, is_not_numeric, safe_get_entry, safe_get_entry_with_default
from utils.encoder import AlchemyEncoder

def admin_get_roles(current_user):
    rolesJson = get_infra_playbook_roles()
    roles = []
    for roleJson in rolesJson:
        roles.append(roleJson["name"])
    return JSONResponse(content = {"roles": roles}, status_code = 200)

def admin_get_environment(current_user, environmentId, db):
    if is_not_numeric(environmentId):
        return JSONResponse(content = {"error": "Invalid environment id"}, status_code = 400)

    env = Environment.getById(environmentId, db)
    if not env:
        return JSONResponse(content = {"message": "environment not found", "i18n_code": "804"}, status_code = 404)
    envJson = json.loads(json.dumps(env, cls = AlchemyEncoder))
    return JSONResponse(content = envJson, status_code = 200)

def admin_import_environment(current_user, env, db):
    envJson = env.file.read()
    env_dict = json.loads(envJson)
    exist_env = Environment.getByPath(env_dict["path"], db)
    if exist_env:
        return JSONResponse(content = {"error": "path already exists", "i18n_code": "808"}, status_code = 409)
    new_env = Environment()
    new_env.name = env_dict["name"]
    new_env.path = env_dict["path"]
    new_env.description = env_dict["description"]
    new_env.roles = env_dict["roles"]
    new_env.subdomains = safe_get_entry(env_dict, "subdomains")
    new_env.environment_template = env_dict["environment_template"]
    new_env.doc_template = env_dict["doc_template"]
    new_env.is_private = env_dict["is_private"]
    new_env.logo_url = safe_get_entry(env_dict, "logo_url")
    new_env.save(db)
    envJson = json.loads(json.dumps(new_env, cls = AlchemyEncoder))
    envJson["id"] = new_env.id
    return JSONResponse(content = envJson, status_code = 200)

def admin_export_environment(current_user, environmentId, db):
    if is_not_numeric(environmentId):
        return JSONResponse(content = {"error": "Invalid environment id"}, status_code = 400)

    env = Environment.getById(environmentId, db)
    if not env:
        return JSONResponse(content = {"message" : "environment not found", "i18n_code": "804"}, status_code = 404)
    env_dict = json.loads(json.dumps(env, cls = AlchemyEncoder))
    envJson = json.dumps(env_dict, indent = 4)

    file_name = "environment-{}.json".format(env_dict["name"])
    with open(file_name, "w") as outfile:
        outfile.write(envJson)

    encoded_string = ""
    with open(file_name, "rb") as json_file:
        encoded_string = base64.b64encode(json_file.read()).decode()
        json_file.close()
    os.remove(file_name)
    return JSONResponse(content = {"file_name": file_name, "blob": str(encoded_string)}, status_code = 200)

def admin_update_environment(current_user, environmentId, payload, db):
    name = payload.name
    path = payload.path
    description = payload.description
    environment_template = payload.environment_template
    doc_template = payload.doc_template
    roles = unmarshall_list_array(payload.roles)
    subdomains = unmarshall_list_array(payload.subdomains)
    is_private = payload.is_private
    logo_url = payload.logo_url

    if is_empty(name):
        return JSONResponse(content = {"error": "environment name is missing", "i18n_code": "805"}, status_code = 400)

    if is_empty(path):
        return JSONResponse(content = {"error": "environment path is missing", "i18n_code": "806"}, status_code = 400)

    if is_not_numeric(environmentId):
        return JSONResponse(content = {"error": "Invalid environment id"}, status_code = 400)

    exist_env = Environment.getByPath(path, db)
    if exist_env and exist_env.id == environmentId:
        return JSONResponse(content = {"error": f"path already exists", "i18n_code": "808"}, status_code = 409)

    Environment.updateEnvironment(environmentId, name, path, description, roles, subdomains, environment_template, doc_template, is_private, logo_url, db)
    return JSONResponse(content = {"message": f"environment successfully updated", "i18n_code": "801"}, status_code = 200)

def admin_remove_environment(current_user, environmentId, db):
    if is_not_numeric(environmentId):
        return JSONResponse(content = {"error": "Invalid environment id"}, status_code = 400)

    env = Environment.getById(environmentId, db)
    if not env:
        return JSONResponse(content = {"message" : "environment not found", "i18n_code": "804"}, status_code = 404)
    Environment.deleteOne(environmentId, db)
    return JSONResponse(content = {"message" : "Environment successfully deleted", "i18n_code": "802"}, status_code = 200)

def admin_add_environment(current_user, payload, db):
    name = payload.name
    path = payload.path
    roles = unmarshall_list_array(payload.roles)
    subdomains = unmarshall_list_array(payload.subdomains)

    if is_empty(name):
        return JSONResponse(content = {"error": "environment name is missing", "i18n_code": "805"}, status_code = 400)

    if is_empty(path):
        return JSONResponse(content = {"error": "environment path is missing", "i18n_code": "806"}, status_code = 400)

    if is_empty(roles):
        return JSONResponse(content = {"error": "environment roles are missing", "i18n_code": "807"}, status_code = 400)

    exist_env = Environment.getByPath(path, db)
    if exist_env:
        return JSONResponse(content = {"error": "path already exists", "i18n_code": "808"}, status_code = 409)

    payload.roles = None
    payload.subdomains = None
    new_env = Environment(**payload.dict())
    new_env.roles = marshall_list_string(roles)
    new_env.subdomains = marshall_list_string(subdomains)
    new_env.save(db)
    envJson = json.loads(json.dumps(new_env, cls = AlchemyEncoder))
    envJson["id"] = new_env.id
    return JSONResponse(content = envJson, status_code = 201)

def admin_get_environments(current_user, db):
    envs = Environment.getAll(db)
    envsJson = json.loads(json.dumps(envs, cls = AlchemyEncoder))
    return JSONResponse(content = envsJson, status_code = 200)
