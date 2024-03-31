import json

from urllib.error import HTTPError
from pulumi import automation as auto
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse

from utils.common import is_empty, is_not_empty, is_numeric
from utils.dns_zones import get_dns_zones
from utils.domain import is_not_subdomain_valid
from utils.images import get_os_image
from utils.dynamic_name import rehash_dynamic_name
from utils.instance import check_exist_instance, check_instance_name_validity, generic_remove_instance, get_server_state, get_virtual_machine, update_instance_status, create_instance, register_instance, refresh_instance, get_virtual_machine, reregister_instance
from utils.logger import log_msg
from utils.dynamic_name import generate_hashed_name
from utils.gitlab import get_gitlab_project, get_gitlab_project_playbooks, get_project_quietly, get_user_project_by_id, get_user_project_by_name, get_user_project_by_url, is_not_project_found_in_gitlab
from utils.encoder import AlchemyEncoder
from utils.provider import exist_provider, get_provider_infos, get_provider_available_instances_by_region_zone
from utils.zone_utils import exists_zone
from utils.observability.cid import get_current_cid

def admin_add_instance(current_user, payload, provider, region, zone, environment, db, bt: BackgroundTasks):
    instance_name = payload.name
    if is_not_subdomain_valid(instance_name):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'instance name is not valid', 
            'i18n_code': 'instance_name_invalid',
            'cid': get_current_cid()
        }, status_code = 400)

    project_id = payload.project_id
    project_name = payload.project_name
    project_url = payload.project_url
    debug = payload.debug
    instance_type = payload.type
    root_dns_zone = payload.root_dns_zone
    email = payload.email
    generate_dns = "false"
    #? Cloud init will mv _gitlab-ci.yml ./.gitlab-ci.yml And create all the roles and playbook
    centralized = "none"

    try:
        if not exist_provider(provider):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'provider does not exist', 
                'i18n_code': '504',
                'cid': get_current_cid()
            }, status_code = 404)
        if is_empty(instance_name):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'please provide instance name', 
                'i18n_code': '1106',
                'cid': get_current_cid()
            }, status_code = 400)
        if is_empty(email):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'please provide an email', 
                'i18n_code': '1102',
                'cid': get_current_cid()
            }, status_code = 400)
        if is_empty(project_id) and is_empty(project_name) and is_empty(project_url):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'please provide a project id or a project name or a project url', 
                'i18n_code': '1107',
                'cid': get_current_cid()
            }, status_code = 400)

        if  len(get_dns_zones())>0:
            generate_dns = "true"
            if is_empty(root_dns_zone):
                root_dns_zone = get_dns_zones()[0]
                log_msg("INFO", "[api_admin_instance] root_dns_zone is empty, taking the default one {}".format(root_dns_zone))
            elif root_dns_zone not in get_dns_zones():
                log_msg("ERROR", "[api_admin_instance] the root dns zone is not valid :{}".format(root_dns_zone))
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'please provide a valid root dns zone', 
                    'i18n_code': '1108',
                    'cid': get_current_cid()
                }, status_code = 400)

        if is_empty(environment):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'environment is missing', 
                'i18n_code': '803',
                'cid': get_current_cid()
            }, status_code = 400)
        if is_empty(instance_type):
            instance_type = get_provider_available_instances_by_region_zone(provider, region, zone)[0]
        else:
            possible_types = get_provider_available_instances_by_region_zone(provider, region, zone)
            if instance_type not in possible_types:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': f'Instance type does not exist', 
                    'i18n_code': '105',
                    'cid': get_current_cid()
                }, status_code = 400)

        possible_regions = get_provider_infos(provider, 'regions')
        if region not in [region['name'] for region in possible_regions]:
            return JSONResponse(content = {
                'status': 'ko',
                'error': f'region does not exist', 
                'i18n_code': '1404',
                'cid': get_current_cid()
            }, status_code = 400)
        if exists_zone(zone, region, possible_regions):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'zone does not exist', 
                'i18n_code': '1110',
                'cid': get_current_cid()
            }, status_code = 400)

        from entities.Environment import Environment
        exist_env = Environment.getByPath(environment, db)
        if not exist_env:
            return JSONResponse(content = {
                'status': 'ko',
                'error': f'environment not found', 
                'i18n_code': '804',
                'cid': get_current_cid()
            }, status_code = 404)
        if not email == current_user.email:
            from entities.User import User
            exist_user = User.getUserByEmail(email, db)
            if not exist_user:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'user not found', 
                    'i18n_code': '304',
                    'cid': get_current_cid()
                }, status_code = 404)
            else:
                userid = exist_user.id
        else:
            email = current_user.email
            userid = current_user.id

        exist_project = None
        if is_not_empty(project_id):
            exist_project = get_user_project_by_id(project_id, userid, db)
            if not exist_project:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'project not found', 
                    'i18n_code': '204',
                    'cid': get_current_cid()
                }, status_code = 404)
        if is_not_empty(project_name):
            exist_project = get_user_project_by_name(project_name, userid, db)
            if not exist_project:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'project not found', 
                    'i18n_code': '204',
                    'cid': get_current_cid()
                }, status_code = 404)
        if is_not_empty(project_url):
            exist_project = get_user_project_by_url(project_url, userid, db)
            if not exist_project:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'project not found', 
                    'i18n_code': '204',
                    'cid': get_current_cid()
                }, status_code = 404)

        gitlab_project = get_project_quietly(exist_project)
        if is_not_project_found_in_gitlab(gitlab_project):
            return JSONResponse(content = {
                'status': 'ko',
                'error': f'project not found with gitlab', 
                'i18n_code': '210',
                'cid': get_current_cid()
            }, status_code = 404)

        project_playbooks = get_gitlab_project_playbooks(project_id, exist_project.gitlab_host, exist_project.access_token)
        check_instance_name_validity(instance_name)
        check_exist_instance(userid, instance_name, db)
        if len(project_playbooks)>0:
            #? Cloud init will contatenante _gitlab-ci.yml in the existing one And create all the missing roles and playbook
            centralized = "true"
            if instance_name in [name.split("playbook-")[1] for name in project_playbooks]:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'playbook already exists', 
                    'i18n_code': '1111',
                    'cid': get_current_cid()
                }, status_code = 404)
        log_msg("DEBUG", "[admin_instance][admin_add_instance] exist_project = {}".format(exist_project))

        hash, hashed_instance_name = generate_hashed_name(instance_name)
        log_msg("DEBUG", "[admin_instance][admin_add_instance] hash = {}, hashed_instance_name = {}".format(hash, hashed_instance_name))

        new_instance = register_instance(hash, provider, region, zone, userid, instance_name.lower(), instance_type, environment, gitlab_project, root_dns_zone, db)
        ami_image = get_os_image(region, zone)
        user_project_json = json.loads(json.dumps(exist_project, cls = AlchemyEncoder))
        env_json = json.loads(json.dumps(exist_env, cls = AlchemyEncoder))

        bt.add_task(create_instance,
            provider,
            ami_image,
            new_instance.id,
            email,
            instance_name,
            hashed_instance_name,
            env_json,
            region,
            zone,
            generate_dns,
            gitlab_project,
            user_project_json,
            instance_type,
            debug,
            centralized,
            root_dns_zone,
            db
        )

        dumpedInstance = json.loads(json.dumps(new_instance, cls = AlchemyEncoder))
        new_instance_json = {**dumpedInstance, "environment": new_instance.environment.name, "path": new_instance.environment.path, 'status': 'ok',"gitlab_project": new_instance.project.url}
        return JSONResponse(content = new_instance_json, status_code = 200)
    except auto.StackAlreadyExistsError as sae:
        log_msg("ERROR", "[admin_instance][admin_add_instance] unexpected StackAlreadyExistsError:{}".format(sae))
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'stack already exists', 
            'i18n_code': '1105',
            'cid': get_current_cid()
        }, status_code = 409)
    except HTTPError as e:
        log_msg("ERROR", "[admin_instance][admin_add_instance] unexpected HTTPError:{}".format(e))
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)
    except Exception as exn:
        error = {"error": f"{exn}", 'status': 'ko', 'cid': get_current_cid()}
        log_msg("ERROR", "[admin_instance][admin_add_instance] unexpected error: type = {}, msg = {}, line = {}".format(type(exn).__name__, exn, exn.__traceback__.tb_lineno))
        return JSONResponse(content = error, status_code = 500)

def admin_attach_instance(bt: BackgroundTasks, current_user, provider, region, zone, project_id, payload, db):
    instance_name = payload.name
    instance_type = payload.type
    debug = payload.debug
    generate_dns = "false"
    #? Will only make a sed on the gitlab-runner
    centralized = "false"

    from entities.Project import Project
    exist_project = Project.getById(project_id, db)
    if is_empty(exist_project):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Project not found', 
            'i18n_code': '204',
            'cid': get_current_cid()
        }, status_code = 404)

    from entities.User import User
    exist_user = User.getUserById(exist_project.userid, db)
    if not exist_user:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'user not found', 
            'i18n_code': '304',
            'cid': get_current_cid()
        }, status_code = 404)

    from entities.Instance import Instance
    userInstance = Instance.findUserInstanceByName(exist_user.id, instance_name, db)
    if not userInstance:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Instance not found', 
            'i18n_code': '104',
            'cid': get_current_cid()
        }, status_code = 404)
    if userInstance.status != 'deleted':
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Instance already running with this playbook', 
            'i18n_code': '127',
            'cid': get_current_cid()
        }, status_code = 404)

    hash = userInstance.hash
    hashed_instance_name = rehash_dynamic_name(instance_name, hash)
    log_msg("DEBUG", "[admin_instance][attach_instance] hash = {}, hashed_instance_name = {}".format(hash, hashed_instance_name))

    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist', 
            'i18n_code': '504',
            'cid': get_current_cid()
        }, status_code = 404)

    project_playbooks = get_gitlab_project_playbooks(exist_project.id, exist_project.gitlab_host, exist_project.access_token)
    if len(project_playbooks) == 0:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Project has no playbooks', 
            'i18n_code': '206',
            'cid': get_current_cid()
        }, status_code = 400)
    if is_empty(instance_name):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'please specify the playbook you want to attach.', 
            'i18n_code': '121',
            'cid': get_current_cid()
        }, status_code = 400)

    if not instance_name in [name.split("playbook-")[1] for name in project_playbooks]:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'playbook not found', 
            'i18n_code': '122',
            'cid': get_current_cid()
        }, status_code = 404)
    if  len(get_dns_zones())>0 and userInstance.root_dns_zone in get_dns_zones():
        generate_dns = 'true'

    if not instance_type or instance_type == '':
        instance_type = get_provider_available_instances_by_region_zone(provider, region, zone)[0]
    else:
        possible_types = get_provider_available_instances_by_region_zone(provider, region, zone)
        if instance_type not in possible_types:
            return JSONResponse(content = {
                'status': 'ko',
                'error': f'Instance type does not exist', 
                'i18n_code': '105',
                'cid': get_current_cid()
            }, status_code = 400)

    possible_regions = get_provider_infos(provider, 'regions')
    if region not in [region['name'] for region in possible_regions]:
        return JSONResponse(content = {
            'status': 'ko',
            'error': f'region does not exist', 
            'i18n_code': '1404',
            'cid': get_current_cid()
        }, status_code = 400)

    if exists_zone(zone, region, possible_regions):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'zone does not exist', 
            'i18n_code': '1110',
            'cid': get_current_cid()
        }, status_code = 400)

    from entities.Environment import Environment
    exist_env = Environment.getById(userInstance.environment_id, db)
    if not exist_env:
        return JSONResponse(content = {
            'status': 'ko',
            'error': f'environment not found', 
            'i18n_code': '804',
            'cid': get_current_cid()
        }, status_code = 404)
    try:
        gitlab_project = get_gitlab_project(project_id, exist_project.gitlab_host, exist_project.access_token)
        reregister_instance(userInstance.id, provider, region, zone, instance_type, userInstance.root_dns_zone, project_id, db)
        ami_image = get_os_image(region, zone)
        user_project_json = json.loads(json.dumps(exist_project, cls = AlchemyEncoder))
        env_json = json.loads(json.dumps(exist_env, cls = AlchemyEncoder))

        bt.add_task(create_instance,
            provider,
            ami_image,
            userInstance.id,
            exist_user.email,
            instance_name,
            hashed_instance_name,
            env_json,
            region,
            zone,
            generate_dns,
            gitlab_project,
            user_project_json,
            instance_type,
            debug,
            centralized,
            userInstance.root_dns_zone,
            db
        )

        dumpedInstance = json.loads(json.dumps(userInstance, cls = AlchemyEncoder))
        new_instance_json = {**dumpedInstance, 'environment': userInstance.environment.name, 'path': userInstance.environment.path, 'gitlab_project': userInstance.project.url}
        return JSONResponse(content = new_instance_json, status_code = 200)
    except auto.StackAlreadyExistsError:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'stack already exists', 
            'i18n_code': '1105',
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
        error = {'error': f'{exn}', 'status': 'ko', 'cid': get_current_cid()}
        return JSONResponse(content = error, status_code = 500)

def admin_get_instance(current_user, instance_id, db):
    if not is_numeric(instance_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid instance id',
            'cid': get_current_cid()
        }, status_code = 400)

    from entities.Instance import Instance
    userInstance = Instance.findInstanceById(instance_id, db)
    if not userInstance:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Instance not found', 
            'i18n_code': '104',
            'cid': get_current_cid()
        }, status_code = 404)

    dumpedInstance = json.loads(json.dumps(userInstance, cls = AlchemyEncoder))
    dumpedProject = json.loads(json.dumps(userInstance.project, cls = AlchemyEncoder))
    instanceJson = {
        **dumpedInstance,
        "environment": userInstance.environment.name if is_not_empty(userInstance.environment) and is_not_empty(userInstance.environment.name) else "unknown",
        "path": userInstance.environment.path if is_not_empty(userInstance.environment) and is_not_empty(userInstance.environment.path) else "unknown",
        "project": {**dumpedProject} if is_not_empty(dumpedProject) else { "name": "unknown" }
    }
    return JSONResponse(content = instanceJson, status_code = 200)

def admin_remove_instance(current_user, instance_id, db, bt: BackgroundTasks):
    if not is_numeric(instance_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid instance id',
            'cid': get_current_cid()
        }, status_code = 400)

    from entities.Instance import Instance
    user_instance = Instance.findInstanceById(instance_id, db)
    result_remove = generic_remove_instance(user_instance, db, bt)
    return JSONResponse(content = result_remove["message"], status_code = result_remove["http_code"])

def admin_refresh_instance(current_user, instance_id, db):
    if not is_numeric(instance_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid instance id',
            'cid': get_current_cid()
        }, status_code = 400)

    from entities.Instance import Instance
    from entities.Environment import Environment
    userInstance = Instance.findInstanceById(instance_id, db)
    if not userInstance:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Instance not found', 
            'i18n_code': '104',
            'cid': get_current_cid()
        }, status_code = 404)
    hashed_instance_name = f'{userInstance.name}-{userInstance.hash}'
    if not get_virtual_machine(userInstance.provider, userInstance.region, userInstance.zone, hashed_instance_name):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Instance not found', 
            'i18n_code': '104',
            'cid': get_current_cid()
        }, status_code = 404)
    exist_env = Environment.getById(userInstance.environment_id, db)
    env_json = json.loads(json.dumps(exist_env, cls = AlchemyEncoder))
    refresh_instance(userInstance.provider, userInstance.id, hashed_instance_name, env_json, userInstance.region, userInstance.zone, db)
    return JSONResponse(content = {
        'status': 'ok',
        'message': 'done'
    }, status_code = 200)

def admin_update_instance(current_user, instance_id, payload, db):
    action = payload.status
    if not is_numeric(instance_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid instance id',
            'cid': get_current_cid()
        }, status_code = 400)
    from entities.Instance import Instance
    userInstance = Instance.findInstanceById(instance_id, db)
    if not userInstance:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Instance not found', 
            'i18n_code': '104',
            'cid': get_current_cid()
        }, status_code = 404)

    server = get_virtual_machine(userInstance.provider, userInstance.region, userInstance.zone, f'{userInstance.name}-{userInstance.hash}')

    if not server:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Instance not found', 
            'i18n_code': '104',
            'cid': get_current_cid()
        }, status_code = 404)

    target_server_id = server["id"]
    possible_actions = ["poweroff", "poweron", "reboot"]
    if not action in possible_actions:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'action doesnt exist', 
            'i18n_code': '106',
            'cid': get_current_cid()
        }, status_code = 400)
    server_state = get_server_state(userInstance.provider, server)
    if action == "poweroff":
        if server_state == "stopped":
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Instance already stopped', 
                'i18n_code': '107',
                'cid': get_current_cid()
            }, status_code = 400)
        if server_state == "rebooting":
            return JSONResponse(content = {
                'status': 'ko',
                'error': "You can't stop the Instance while rebooting", 
                'i18n_code': '108',
                'cid': get_current_cid()
            }, status_code = 400)
        if server_state == "starting":
            return JSONResponse(content = {
                'status': 'ko',
                'error': "You can't stop the Instance while starting", 
                'i18n_code': '109',
                'cid': get_current_cid()
            }, status_code = 400)
        if server_state == "stopping":
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Instance already stopping', 
                'i18n_code': '110',
                'cid': get_current_cid()
            }, status_code = 400)
    if action == "poweron":
        if server_state == "running":
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Instance already running', 
                'i18n_code': '111',
                'cid': get_current_cid()
            }, status_code = 400)
        if server_state == "rebooting":
            return JSONResponse(content = {
                'status': 'ko',
                'error': "You can't start the Instance while rebooting", 
                'i18n_code': '112',
                'cid': get_current_cid()
            }, status_code = 400)
        if server_state == "starting":
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Instance already starting', 
                'i18n_code': '113',
                'cid': get_current_cid()
            }, status_code = 400)
        if server_state == "stopping":
            return JSONResponse(content = {
                'status': 'ko',
                'error': "You can't start the Instance while stopping", 
                'i18n_code': '114',
                'cid': get_current_cid()
            }, status_code = 400)
    if action == "reboot":
        if server_state == "stopped":
            return JSONResponse(content = {
                'status': 'ko',
                'error': "You can't reboot the Instance when it is stopped", 
                'i18n_code': '115',
                'cid': get_current_cid()
            }, status_code = 400)
        if server_state == "rebooting":
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Instance already rebooting', 
                'i18n_code': '116',
                'cid': get_current_cid()
            }, status_code = 400)
        if server_state == "starting":
            return JSONResponse(content = {
                'status': 'ko',
                'error': "You can't reboot the Instance while starting", 
                'i18n_code': '117',
                'cid': get_current_cid()
            }, status_code = 400)
        if server_state == "stopping":
            return JSONResponse(content = {
                'status': 'ko',
                'error': "You can't reboot the Instance while stopping", 
                'i18n_code': '118',
                'cid': get_current_cid()
            }, status_code = 400)
    try:
        if userInstance.status == "active" and action == "activate":
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'instance already active', 
                'i18n_code': '119',
                'cid': get_current_cid()
            }, status_code = 400)
        update_instance_status(userInstance, target_server_id, action, db)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'instance successfully updated', 
            'i18n_code': '101'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)

def admin_get_instances(current_user, provider, region, db):
    from entities.Instance import Instance
    userRegionInstances = Instance.getAllInstancesByRegion(provider, region, db)
    userRegionInstancesJson = json.loads(json.dumps(userRegionInstances, cls = AlchemyEncoder))
    return JSONResponse(content = userRegionInstancesJson, status_code = 200)

def admin_get_user_instances(current_user, provider, region, user_id, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist', 
            'i18n_code': '504',
            'cid': get_current_cid()
        }, status_code = 404)
    from entities.Instance import Instance
    userRegionInstances = Instance.getAllUserInstancesByRegion(provider, region, user_id, db)
    userRegionInstancesJson = json.loads(json.dumps(userRegionInstances, cls = AlchemyEncoder))
    return JSONResponse(content = userRegionInstancesJson, status_code = 200)
