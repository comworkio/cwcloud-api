import base64
import json
from typing import Literal, Optional

from fastapi import UploadFile
from fastapi.responses import JSONResponse

from entities.Environment import Environment
from utils.common import is_empty, is_not_numeric, safe_get_entry, is_not_empty_key, is_not_empty
from utils.encoder import AlchemyEncoder
from utils.file import quiet_remove
from utils.gitlab import get_helm_charts, get_infra_playbook_roles
from utils.list import marshall_list_string, unmarshall_list_array
from utils.observability.cid import get_current_cid
from utils.logger import log_msg


def admin_get_roles(current_user):
    error_response, infra_playbook_roles = get_infra_playbook_roles()
    roles = []

    if is_not_empty(error_response):
        return error_response

    if not isinstance(infra_playbook_roles, list):
        log_msg("DEBUG", "[admin_get_roles] Unexpected role format in data, infra_playbook_roles={}".format(infra_playbook_roles))
        return JSONResponse(content={
            "status": "ko",
            "message": "Unexpected role format in data",
            "i18n_code": "unexpected_role_format",
            "cid": get_current_cid()
        }, status_code=500)

    for role in infra_playbook_roles:
        if is_not_empty_key(role, "name"):
            roles.append(role["name"])

    return JSONResponse(content = {"roles": roles}, status_code = 200)

def admin_get_environment(environment_id, db):
    if is_not_numeric(environment_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid environment id',
            'cid': get_current_cid()
        }, status_code = 400)

    env = Environment.getById(environment_id, db)
    if not env:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'environment not found', 
            'i18n_code': 'environment_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    env_json = json.loads(json.dumps(env, cls = AlchemyEncoder))
    return JSONResponse(content = env_json, status_code = 200)

def admin_get_k8s_environment(environment_id, db):
    if is_not_numeric(environment_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid environment id',
            'cid': get_current_cid()
        }, status_code = 400)

    env = Environment.getById(environment_id, db)
    if not env or env.type != "k8s":
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'environment not found', 
            'i18n_code': 'environment_not_found',
            'cid': get_current_cid()
        }, status_code = 404)

    env_json = json.loads(json.dumps(env, cls = AlchemyEncoder))
    return JSONResponse(content = env_json, status_code = 200)

def admin_import_environment(env: UploadFile, db):
    env_json = env.file.read()
    env_dict = json.loads(env_json)
    exist_env = Environment.getByPath(env_dict["path"], db)
    if exist_env:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'path already exists', 
            'i18n_code': 'path_already_exist',
            'cid': get_current_cid()
        }, status_code = 409)
    elif not env_dict["type"] in ["vm", "k8s"]:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid environment type', 
            'i18n_code': 'invalid_environment_type',
            'cid': get_current_cid()
        }, status_code = 400)
    new_env: Environment = Environment(**env_dict)
    new_env.id = None
    new_env.save(db)
    env_json = json.loads(json.dumps(new_env, cls = AlchemyEncoder))
    env_json["id"] = new_env.id
    return JSONResponse(content = env_json, status_code = 200)

def admin_export_environment(current_user, environment_id, db):
    if is_not_numeric(environment_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid environment id',
            'cid': get_current_cid()
        }, status_code = 400)

    env = Environment.getById(environment_id, db)
    if not env:
        return JSONResponse(content = {
            'status': 'ko',
            'message' : 'environment not found', 
            'i18n_code': 'environment_not_found',
            'cid': get_current_cid()
        }, status_code = 404)

    env_dict = json.loads(json.dumps(env, cls = AlchemyEncoder))
    env_json = json.dumps(env_dict, indent = 4)

    file_name = "environment-{}.json".format(env_dict["name"])
    with open(file_name, "w") as outfile:
        outfile.write(env_json)

    encoded_string = ""
    with open(file_name, "rb") as json_file:
        encoded_string = base64.b64encode(json_file.read()).decode()
        json_file.close()

    quiet_remove(file_name)
    return JSONResponse(content = {
        'status': 'ok',
        'file_name': file_name, 
        'blob': str(encoded_string)
    }, status_code = 200)

def admin_update_environment(environment_id, payload, db):
    name = payload.name
    path = payload.path
    description = payload.description
    environment_template = payload.environment_template
    doc_template = payload.doc_template
    roles = unmarshall_list_array(payload.roles)
    subdomains = unmarshall_list_array(payload.subdomains)
    is_private = payload.is_private
    logo_url = payload.logo_url
    args = verify_env_args(payload.args)
    if is_empty(name):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'environment name is missing', 
            'i18n_code': 'environment_name_missing',
            'cid': get_current_cid()
        }, status_code = 400)

    if is_empty(path):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'environment path is missing', 
            'i18n_code': 'environment_path_missing',
            'cid': get_current_cid()
        }, status_code = 400)

    if is_not_numeric(environment_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid environment id',
            'cid': get_current_cid()
        }, status_code = 400)

    exist_env = Environment.getByPath(path, db)
    if exist_env and exist_env.id == environment_id:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'path already exists', 
            'i18n_code': 'path_already_exist',
            'cid': get_current_cid()
        }, status_code = 409)

    Environment.updateEnvironment(environment_id, name, path, description, roles, subdomains, environment_template, doc_template, is_private, logo_url, args, db)
    return JSONResponse(content = {
        'status': 'ok',
        'message': 'environment successfully updated', 
        'i18n_code': 'environment_updated'
    }, status_code = 200)

def admin_remove_environment(environment_id, db):
    if is_not_numeric(environment_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid environment id',
            'cid': get_current_cid()
        }, status_code = 400)

    env = Environment.getById(environment_id, db)
    if not env:
        return JSONResponse(content = {
            'status': 'ko',
            'message' : 'environment not found', 
            'i18n_code': 'environment_not_found',
            'cid': get_current_cid()
        }, status_code = 404)

    Environment.deleteOne(environment_id, db)
    return JSONResponse(content = {
        'status': 'ok',
        'message' : 'Environment successfully deleted', 
        'i18n_code': 'environment_deleted'
    }, status_code = 200)

def admin_add_environment(payload, db):
    name = payload.name
    path = payload.path
    roles = unmarshall_list_array(payload.roles)
    subdomains = unmarshall_list_array(payload.subdomains)
    args = payload.args
    args = verify_env_args(args)

    if is_empty(name):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'environment name is missing', 
            'i18n_code': 'environment_name_missing',
            'cid': get_current_cid()
        }, status_code = 400)

    if is_empty(path):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'environment path is missing', 
            'i18n_code': 'environment_path_missing',
            'cid': get_current_cid()
        }, status_code = 400)

    if is_empty(roles):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'environment roles are missing', 
            'i18n_code': 'environment_roles_missing',
            'cid': get_current_cid()
        }, status_code = 400)

    exist_env = Environment.getByPath(path, db)
    if exist_env:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'path already exists', 
            'i18n_code': 'path_already_exist',
            'cid': get_current_cid()
        }, status_code = 409)

    payload.roles = None
    payload.subdomains = None
    payload.args = None
    new_env = Environment(**payload.dict())
    new_env.roles = marshall_list_string(roles)
    new_env.subdomains = marshall_list_string(subdomains)
    new_env.args = args
    new_env.type = "vm"
    new_env.save(db)
    env_json = json.loads(json.dumps(new_env, cls = AlchemyEncoder))
    env_json["id"] = new_env.id

    return JSONResponse(content = env_json, status_code = 201)

def admin_get_environments(type:Literal["vm", "k8s", "all"], page, limit, db):
    if (page is None and limit is None) or (page < 0 or limit < 0):
        if(type == "all"):
            envs = Environment.getAll(db)
        else:
            envs = Environment.getByType(type, db)
    else:
        if(type == "all"):
            envs = Environment.getAllPaginated(page, limit, db)
        else:
            envs = Environment.getByTypePaginated(type, page, limit, db)
    envs_json = json.loads(json.dumps(envs, cls=AlchemyEncoder))
    return JSONResponse(content=envs_json, status_code=200)

def admin_add_k8s_environment(env_data, db):
    env = Environment(name=env_data.name,
                    type="k8s",
                    description=env_data.description,
                    path=env_data.path,
                    logo_url=env_data.logo_url,
                    is_private=env_data.is_private,
                    external_roles=json.dumps([chart.__dict__ for chart in env_data.external_charts]) if  env_data.external_charts else None,
                    roles=env_data.charts,
                    environment_template=env_data.environment_template,
                    doc_template=env_data.doc_template)

    args = verify_env_args(env_data.args)
    env.args = args
    env.save(db)
    return JSONResponse(content = {
        'status': 'ok',
        'message': 'Environment created successfully', 
        'id': env.id
    }, status_code = 201)

def admin_delete_k8s_environment(environment_id, db):
    if is_not_numeric(environment_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid environment id',
            'cid': get_current_cid()
        }, status_code = 400)

    env: Environment  = Environment.getById(environment_id, db)
    if not env or env.type != "k8s":
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'environment not found', 
            'i18n_code':'environment_not_found',
            'cid': get_current_cid()
        }, status_code = 404)

    env.deleteOne(environment_id, db)
    return JSONResponse(content = {
        'status': 'ok',
        'message': 'environment deleted'
    }, status_code = 200)

def admin_update_k8s_environment(environment_id, env_data, db):
    env: Environment  = Environment.getById(environment_id, db)
    if not env or env.type != "k8s":
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'environment not found', 
            'i18n_code':'environment_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    env.name = env_data.name
    env.description = env_data.description
    env.path = env_data.path    
    env.logo_url = env_data.logo_url
    env.is_private = env_data.is_private
    env.roles = env_data.charts
    env.environment_template = env_data.environment_template
    env.doc_template = env_data.doc_template
    env.external_roles=json.dumps([chart.__dict__ for chart in env_data.external_charts]) if  env_data.external_charts else None

    args = verify_env_args(env_data.args)
    env.args = args
    env.save(db)
    return JSONResponse(content = {
        'status': 'ok',
        'message': 'environment updated',
        'i18n_code':'environment_updated'
    }, status_code = 200)

def get_charts():
    error_response, charts = get_helm_charts()
    
    if is_not_empty(error_response):
        return error_response
    
    if not isinstance(charts, list):
        log_msg("DEBUG", "[get_charts] Unexpected chart format in data, charts={}".format(charts))
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'Unexpected chart format in data',
            'i18n_code': 'unexpected_chart_format',
            'cid': get_current_cid()
        }, status_code = 500)
    
    return JSONResponse(content = charts, status_code = 200)

def verify_env_args(args:Optional[list[str]] = None):
    if(args is None):
        args = []
    try:
        return json.dumps(args)
    except Exception:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'args is not a valid json list', 
            'i18n_code': 'args_not_valid_json_list',
            'cid': get_current_cid()
        }, status_code = 400)
