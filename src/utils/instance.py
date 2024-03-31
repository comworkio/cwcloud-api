import os
import importlib

from urllib.error import HTTPError
from jinja2 import Environment, FileSystemLoader
from pulumi import automation as auto
from datetime import datetime
from time import sleep
from fastapi import BackgroundTasks

from entities.Instance import Instance

from utils.api_url import get_api_url
from utils.exec import exec_cmd
from utils.file import quiet_remove
from utils.gitlab import delete_runner, get_project_runners, inject_default_credentials_to_url, inject_git_credentials_to_url
from utils.bytes_generator import generate_random_bytes, is_disable_dynamic_names
from utils.consumption import generate_instance_consumption
from utils.provider import get_driver
from utils.list import unmarshall_list_array
from utils.mail import send_create_instance_email
from utils.logger import log_msg
from utils.common import is_disabled, is_empty, is_false, is_not_empty
from utils.constants import MAX_RETRY, WAIT_TIME
from utils.observability.cid import get_current_cid

def check_exist_instance(userId, instance_name, db):
    from entities.Instance import Instance
    userInstance = Instance.findUserAvailableInstanceByName(userId, instance_name, db)
    if userInstance:
        raise HTTPError("123", 409, 'instance already exists', hdrs = {"i18n_code": "123"}, fp = None)

    return False

def check_instance_name_validity(name):
    special_characters = " !\"#$%&'()*+,./:;<=>?@[\]^_`{|}~"
    if any(c in special_characters for c in name):
        raise HTTPError("1118", 400, 'name contains invalid caracters', hdrs = {"i18n_code": "1118"}, fp = None)
    if len(name)>50:
        raise HTTPError("1119", 400, 'name is too long', hdrs = {"i18n_code": "1119"}, fp = None)

def reregister_instance(instanceId, provider, region, zone, instance_type, root_dns_zone, project_id, db):
    from entities.Instance import Instance
    Instance.recreateInstanceInfo(instanceId, provider, region, zone, instance_type, "starting", "Null", root_dns_zone, project_id, db)

def register_instance(hash, provider, region, zone, userid, instance_name, instance_type, environment, gitlab_project, root_dns_zone, db):
    from entities.Instance import Instance
    from entities.Environment import Environment
    from entities.User import User
    from entities.Project import Project
    new_instance = Instance()
    new_instance.hash = hash
    new_instance.name = instance_name
    new_instance.type = instance_type
    new_instance.region = region
    new_instance.zone = zone
    new_instance.provider = provider
    new_instance.root_dns_zone = root_dns_zone
    new_instance.save(db)
    env = Environment.getByPath(environment, db)
    env.instances.append(new_instance)
    env.save(db)
    project = Project.getById(gitlab_project['id'], db)
    project.instances.append(new_instance)
    project.save(db)
    user = User.getUserById(userid, db)
    user.instances.append(new_instance)
    user.save(db)
    return new_instance

def get_server_state(provider, server):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    return ProviderDriver().get_server_state(server)

def get_virtual_machine(provider, region, zone, instance_name):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    return ProviderDriver().get_virtual_machine(region, zone, instance_name)

def create_instance(provider, ami_image, instance_id, user_email, instance_name, hashed_instance_name, environment, instance_region, instance_zone, generate_dns, gitlab_project, user_project, instance_type, debug, centralized, root_dns_zone, db):
    root_password = generate_random_bytes(20)
    access_password = generate_random_bytes(20)
    setup_ansible(user_email, gitlab_project, user_project, instance_name, hashed_instance_name, environment, centralized, root_password, access_password, generate_dns, root_dns_zone)

    try:
        if is_false(debug):
            send_create_instance_email(user_email, gitlab_project['http_url_to_repo'], hashed_instance_name, environment, access_password, root_dns_zone)
    except Exception as exn:
        log_msg("WARN", "[instance][create_instance] Gitlab user {} is already a member of this project due to a greater inherited membership., e = {}".format(user_email, exn))

    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    cloud_init_script = ProviderDriver().cloud_init_script()

    config_cloud_init(instance_id, instance_name, user_project, gitlab_project['name'], gitlab_project['http_url_to_repo'], debug, centralized, provider)
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    log_msg("DEBUG", "[create_instance] creating instance hashed_instance_name = {}".format(hashed_instance_name))
    result = ProviderDriver().create_instance(instance_id, ami_image, hashed_instance_name, environment, instance_region, instance_zone, instance_type, generate_dns, root_dns_zone)
    log_msg("DEBUG", "[create_instance] driver result = {}".format(result))
    if "ip" in result:
        Instance.updateInstanceIp(instance_id, result['ip'], db)
    quiet_remove(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', cloud_init_script)))

def refresh_instance(provider, instance_id, hashed_instance_name, environment, instance_region, instance_zone, db):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    result = ProviderDriver().refresh_instance(instance_id, hashed_instance_name, environment, instance_region, instance_zone)
    if "type" in result and "ip" in result:
        Instance.updateTypeAndIp(instance_id, result['type'], result['ip'], db)

def clean_up_ansible_config_files():
    quiet_remove(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'ansible', 'instance_name.md.j2')))
    quiet_remove(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'ansible', 'instance_name.yml.j2')))

def prepare_ansible_config_files(env):
    envFile = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'ansible', 'instance_name.yml.j2'))
    file = open(envFile, "w")
    file.write(env['environment_template'])
    file.close()

    envFile = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'ansible', 'instance_name.md.j2'))
    file = open(envFile, "w")
    file.write(env['doc_template'])
    file.close()

def setup_ansible(user_email, gitlab_project, user_project, instance_name, hashed_instance_name, environment, centralized, root_password, access_password, generate_dns, _root_dns_zone):
    scriptPath = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'ansible_script.sh'))
    cloned_repo = os.getenv('GIT_PLAYBOOK_REPO_URL')
    if is_disabled(cloned_repo):
        return

    cloned_repo_credential = inject_default_credentials_to_url(cloned_repo)
    created_project_remote = inject_git_credentials_to_url(gitlab_project['http_url_to_repo'], user_project['git_username'], user_project['access_token'])
    username = user_email.split('@')[0]
    splittedRemote = gitlab_project['http_url_to_repo'].split('//')
    gitlab_project_remote = 'https://{}:{}@{}'.format(username, user_project['access_token'], splittedRemote[1])
    if is_disabled(gitlab_project_remote):
        return

    git_username = os.getenv('GIT_USERNAME')
    git_email = os.getenv('GIT_EMAIL')

    if is_empty(root_password):
        root_password = generate_random_bytes(20)

    if is_empty(access_password):
        access_password = generate_random_bytes(20)

    root_dns_zone = ""

    prepare_ansible_config_files(environment)

    if is_not_empty(_root_dns_zone):
        root_dns_zone = _root_dns_zone

    bashCommand = ["bash", scriptPath,
                    '-e', environment['path'],
                    '-g', gitlab_project['name'],
                    '-n', instance_name,
                    '-x', hashed_instance_name,
                    '-c', cloned_repo_credential,
                    '-o', created_project_remote,
                    '-j', user_project['gitlab_host'],
                    '-q', generate_dns,
                    '-m', git_email,
                    '-b', user_email,
                    '-u', git_username,
                    '-l', gitlab_project_remote,
                    '-p', root_password,
                    '-t', gitlab_project['runners_token'],
                    '-z', access_password,
                    '-d', root_dns_zone,
                    '-s', centralized]

    bashCommand.extend(unmarshall_list_array(environment['roles']))
    exec_cmd(bashCommand)
    clean_up_ansible_config_files()

def config_cloud_init(instance_id, instance_name, user_project, gitlab_project_name, gitlab_project_url, debug, centralized, provider):
    env = Environment(loader = FileSystemLoader('./'), trim_blocks = True, lstrip_blocks = True)
    dynamic_repo = inject_git_credentials_to_url(gitlab_project_url, user_project['git_username'], user_project['access_token'])

    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    cloud_init_script = ProviderDriver().cloud_init_script()
    template = env.get_template(f'{cloud_init_script}.j2')

    git_username = os.getenv('GIT_USERNAME')
    git_email = os.getenv('GIT_EMAIL')

    data = {
        "dynamic_repo": dynamic_repo,
        "git_username": git_username,
        "git_email": git_email,
        "instance_id": instance_id,
        "gitlab_project_name": gitlab_project_name,
        "instance_name": instance_name,
        "debug": debug,
        "centralized": centralized,
        "API_URL": get_api_url()
    }

    cloudInitPath = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', cloud_init_script))
    file = open(cloudInitPath, "w")
    file.write(template.render(data))
    file.close()

def delete_instance(hash, projectName, environment, retry = 0):
    try:
        if retry >= MAX_RETRY:
            log_msg("WARN", "[delete_instance] max retries has been reached : retry = {}, projectName = {}, environment = {}".format(retry, projectName, environment))
            return

        if retry > 0:
            waiting_time = WAIT_TIME * retry
            log_msg("DEBUG", "[delete_instance] waiting: projectName = {}, environment = {}, wait = {}".format(projectName, environment, waiting_time))
            sleep(waiting_time)

        # FIXME the stack name is probably something else, that's why the instance are not always deleted on the cloud side
        # In the drivers we have sanitize_project_name(environment['path'])
        stack = auto.select_stack(f'{projectName}-{hash}', environment, program = delete_instance)
        stack.destroy()
    except Exception as e:
        log_msg("WARN", "[delete_instance] trying again because of this error: projectName = {}, environment = {}, error = {}".format(projectName, environment, e))
        delete_instance(hash, projectName, environment, retry + 1)

def update_virtual_machine_status(provider, region, zone, server_id, action):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    return ProviderDriver().update_virtual_machine_status(region, zone, server_id, action)

def update_instance_status(instance, server_id, action, db):
    if not action == 'activate' and not action == 'delete':
        update_virtual_machine_status(instance.provider, instance.region, instance.zone, server_id, action)

    switcher = {
        "poweroff": "poweredoff",
        "poweron": "active",
        "reboot": "active",
        "activate": "active",
        "delete": "deleted"
    }

    from entities.Instance import Instance
    Instance.updateStatus(instance.id, switcher.get(action), db)
    nowDate = datetime.now()
    if action == 'poweroff' or action == 'delete':
        # create consumption
        try:
            instance_modification_date = datetime.fromisoformat(str(instance.modification_date))
            if is_not_empty(instance.user):
                generate_instance_consumption(instance.user.id, instance, instance_modification_date, nowDate, True, db)
        except Exception as e:
            message = e
            raise HTTPError("706", 400, message, hdrs = {"i18n_code": "706"}, fp = None)
    else:
        Instance.updateModificationDate(instance.id, nowDate.isoformat(), db)

def generic_remove_instance(userInstance, db, bt: BackgroundTasks):
    if is_empty(userInstance):
        return {
            'status': 'ko',
            'error': 'Instance not found',
            'i18n_code': "104",
            'http_code': 404,
            'cid': get_current_cid()
        }

    server = None
    target_server_id = "none"

    try:
        server = get_virtual_machine(userInstance.provider, userInstance.region, userInstance.zone, rehash_instance_name(userInstance.name, userInstance.hash))
    except Exception as e:
        log_msg("WARN", "[remove_instance] unexpected error (get_virtual_machine) : {}".format(e))

    if is_not_empty(server):
        target_server_id = server['id']
        server_state = get_server_state(userInstance.provider, server)
        if not server_state in ['running', 'stopped']:
            return {
                'status': 'ko',
                'error': "You can't delete the instance while it is not running or stopped",
                'i18n_code': '120',
                'http_code': 400,
                'cid': get_current_cid()
            }
    try:
        try:
            bt.add_task(delete_instance, userInstance.hash, userInstance.name, userInstance.environment.path)
        except Exception as ae:
            log_msg("WARN", "[generic_remove_instance] unexpected error (delete_instance) : {}".format(ae))

        runners = get_project_runners(userInstance.project.id, userInstance.project.gitlab_host, userInstance.project.access_token) if is_not_empty(userInstance.project) else []
        filtered_runners = [runner for runner in runners if runner['ip_address'] == userInstance.ip_address]

        if len(filtered_runners) > 0:
            delete_runner(filtered_runners[0]['id'], userInstance.project.gitlab_host, userInstance.project.access_token)

        update_instance_status(userInstance, target_server_id, "delete", db)
        return {
            'status': 'ko',
            'message': 'instance state successfully deleted',
            'i18n_code': '102',
            'http_code': 200,
            'cid': get_current_cid()
        }

    except HTTPError as e:
        return {
            'status': 'ko',
            'error': e.msg,
            'i18n_code': e.headers['i18n_code'],
            'http_code': e.code,
            'cid': get_current_cid()
        }

def rehash_instance_name(instance_name, hash):
    return instance_name if is_disable_dynamic_names() or is_empty(hash) else "{}-{}".format(is_disable_dynamic_names, hash)
