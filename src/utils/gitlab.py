import os
import base64
import secrets
import gitlab
import requests
import yaml
from fastapi.responses import JSONResponse

from datetime import datetime, timedelta
from urllib.error import HTTPError
from urllib.parse import urlparse

from utils.api_url import is_url_not_responding
from utils.bytes_generator import generate_random_bytes
from utils.common import exists_entry, is_disabled, is_empty, is_empty_key, is_not_empty, is_not_empty_key, safe_compare_entry, safe_contain_entry, is_response_ok
from utils.logger import log_msg
from utils.mail import send_email

GITLAB_URL = os.environ['GITLAB_URL']
GIT_USERNAME = os.getenv('GIT_USERNAME')
GIT_EMAIL = os.getenv('GIT_EMAIL')
GIT_DEFAULT_TOKEN = os.getenv('GIT_PRIVATE_TOKEN')
GITLAB_PROJECTID_ISSUES = os.getenv('GITLAB_PROJECTID_ISSUES')

timeout_value = int(os.getenv("TIMEOUT", "60"))

def check_gitlab_url(gitlab_url):
    if is_not_public_instance(gitlab_url) and is_url_not_responding(gitlab_url):
        raise HTTPError("gitlab_url_not_available", 400, "gitlab url not available", hdrs = {"i18n_code": "gitlab_url_not_available"}, fp = None)

def is_not_public_instance(gitlab_url):
    return not is_public_instance(gitlab_url)

def is_public_instance(gitlab_url):
    return gitlab_url in get_public_instances()

def get_public_instances():
    config_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'cloud_environments.yml'))
    result = ["https://gitlab.com"]
    with open(config_path, "r") as stream:
        loaded_data = yaml.safe_load(stream)
        if is_not_empty(loaded_data) and 'gitlab_public_instances' in loaded_data and is_not_empty(loaded_data['gitlab_public_instances']):
            result = loaded_data['gitlab_public_instances']

    log_msg("INFO", "[gitlab][get_public_instances] gitlab loaded public instances are : {}".format(result))
    return result

def create_project_label(name, color):
    if is_disabled(GITLAB_PROJECTID_ISSUES):
        return {}

    label_json = {
        "name": name,
        "color": color
    }

    check_gitlab_url(GITLAB_URL)
    requests.post(f'{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECTID_ISSUES}/labels', json=label_json, headers={"PRIVATE-TOKEN": GIT_DEFAULT_TOKEN}, timeout=timeout_value)

def check_create_labels_support():
    if is_disabled(GITLAB_PROJECTID_ISSUES):
        return {}

    check_gitlab_url(GITLAB_URL)

    project_labels_reponse = requests.get(f'{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECTID_ISSUES}/labels', headers={"PRIVATE-TOKEN": GIT_DEFAULT_TOKEN}, timeout=timeout_value)
    project_labels = project_labels_reponse.json()

    if is_not_empty_key(project_labels, "error"):
        log_msg("WARN", "[check_create_labels_support] There's an error when fetching the labels: error = {}".format(project_labels['error']))
        return {}

    label_names = [label['name'] for label in project_labels]
    if not 'support' in label_names:
        create_project_label('support', "#00b140")
    if not 's-low' in label_names:
        create_project_label('s-low', "#eee600")
    if not 's-medium' in label_names:
        create_project_label('s-medium', "#ed9121")
    if not 's-high' in label_names:
        create_project_label('s-high', "#ff0000")

def get_relevant_labels_from_issue(issue):
   if is_not_empty_key(issue, "error"):
       return []

   return [label for label in issue['labels'] if label not in ['doing', 'todo', 'review']]

def close_gitlab_issue(issue_id):
    check_gitlab_url(GITLAB_URL)

    if is_disabled(GITLAB_PROJECTID_ISSUES) or is_empty(issue_id):
        return {}

    issue = requests.get(f'{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECTID_ISSUES}/issues/{issue_id}', headers={"PRIVATE-TOKEN": GIT_DEFAULT_TOKEN}, timeout=timeout_value).json()
    if is_not_empty_key(issue, "error"):
        log_msg("WARN", "[close_gitlab_issue] There's an error when fetching the issue: error = {}".format(issue['error']))
        return {}

    new_labels = get_relevant_labels_from_issue(issue)
    data = {
        "state_event": "close",
        "labels": new_labels
    }

    requests.put(f'{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECTID_ISSUES}/issues/{issue_id}', json=data, headers={"PRIVATE-TOKEN": GIT_DEFAULT_TOKEN}, timeout=timeout_value)

def reopen_gitlab_issue(issue_id):
    if is_disabled(GITLAB_PROJECTID_ISSUES) or is_empty(issue_id):
        return {}

    check_gitlab_url(GITLAB_URL)
    issue = requests.get(f'{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECTID_ISSUES}/issues/{issue_id}', headers={"PRIVATE-TOKEN": GIT_DEFAULT_TOKEN}, timeout=timeout_value).json()
    if is_not_empty_key(issue, "error"):
        log_msg("WARN", "[reopen_gitlab_issue] There's an error when fetching the issue: error = {}".format(issue['error']))
        return {}

    new_labels = get_relevant_labels_from_issue(issue)
    new_labels.append("todo")
    data = {
        "state_event": "reopen",
        "labels": new_labels
    }

    requests.put(f'{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECTID_ISSUES}/issues/{issue_id}', json=data, headers={"PRIVATE-TOKEN": GIT_DEFAULT_TOKEN}, timeout=timeout_value)

def add_gitlab_issue(ticketId, user_email, title, description, severity, product):
    if is_disabled(GITLAB_PROJECTID_ISSUES):
        return None

    check_gitlab_url(GITLAB_URL)
    check_create_labels_support()

    issue_description = "* __Ticket:__ [# {}]({}/admin/support/{}) \n\n * __User:__ {} \n\n * __Service:__ {} \n\n * __Description:__ {}".format(ticketId, os.getenv("DOMAIN"), ticketId, user_email, product, description)

    data = {
        "title": title,
        "description": issue_description,
        "labels": "todo, support, s-{} ".format(severity)
    }

    res = requests.post(f'{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECTID_ISSUES}/issues', json=data, headers={"PRIVATE-TOKEN": GIT_DEFAULT_TOKEN}, timeout=timeout_value)
    issue = res.json()

    if is_not_empty_key(issue, "error"):
        log_msg("WARN", "[add_gitlab_issue] There's an error when creating an issue: error = {}".format(issue['error']))
        return None

    if is_empty_key(issue, "iid"):
        log_msg("WARN", "[add_gitlab_issue] No iid found on the issue: issue = {}".format(issue))
        return None

    return issue['iid']

def add_gitlab_issue_comment(issue_id, user_email, message):
    if is_disabled(GITLAB_PROJECTID_ISSUES):
        return {}

    check_create_labels_support()
    issue_comment = "* __User:__ {} \n\n * __Message:__ {}".format(user_email, message)
    data = {
        "body": issue_comment,
    }
    check_gitlab_url(GITLAB_URL)
    requests.post(f'{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECTID_ISSUES}/issues/{issue_id}/notes', json=data, headers={"PRIVATE-TOKEN": GIT_DEFAULT_TOKEN}, timeout=timeout_value)

def inject_git_credentials_to_url(remote, username, token):
    splittedRemote = remote.split('//')
    return f'{splittedRemote[0]}//{username}:{token}@{splittedRemote[1]}'

def inject_default_credentials_to_url(remote):
    splittedRemote = remote.split('//')
    return f'{splittedRemote[0]}//{GIT_USERNAME}:{GIT_DEFAULT_TOKEN}@{splittedRemote[1]}'

def create_gitlab_user(user_email):
    if is_public_instance(GITLAB_URL):
        return

    check_gitlab_url(GITLAB_URL)
    user_password = generate_random_bytes(24)
    gl = gitlab.Gitlab(url = "{}/".format(GITLAB_URL), private_token = GIT_DEFAULT_TOKEN)

    try:
        if not gl.users.list(search = user_email):
            name = user_email.split('@')[0]

            user_data = {
                'email': user_email,
                'username': name,
                'name': name,
                'password': user_password
            }

            gl.users.create(user_data)

            subject = "GitLab Credentials"
            message = "New Gitlab account credentials: <ul> <li>user_name: "+ name\
                    + "<li> password : " + user_password + "</ul>"
            send_email(user_email, message, subject)
    except gitlab.exceptions.GitlabCreateError as exn:
       log_msg("WARN", "[gitlab][create_gitlab_user] The gitlab user already exists: e.code = {}, e.msg = {}".format(exn.response_code, exn.error_message))

def attach_default_gitlab_project_to_user(projectid, user_email):
    check_gitlab_url(GITLAB_URL)
    if is_disabled(GIT_DEFAULT_TOKEN):
        return

    attach_gitlab_project_to_user(projectid, user_email, GITLAB_URL, GIT_DEFAULT_TOKEN)

def detach_user_gitlab_project(projectid, user_email):
    check_gitlab_url(GITLAB_URL)
    gitlab_host = GITLAB_URL
    if is_disabled(GIT_DEFAULT_TOKEN):
        return

    gl = gitlab.Gitlab(url = "{}/".format(gitlab_host), private_token = GIT_DEFAULT_TOKEN)
    project = gl.projects.get(projectid)
    # add user as gitlab project member
    users = gl.users.list(search = user_email)
    try:
        if len(users) == 0:
            log_msg("WARN", "user {} not found".format(user_email))
        log_msg("INFO", "[gitlab][detach_gitlab_project_to_user] gitlab_user_id = {}".format(users[0].id))
        project.members.delete(users[0].id)
    except Exception as exn:
        log_msg("WARN", "[gitlab][attach_gitlab_project_to_user] Gitlab user {} is already a member of this project due to a greater inherited membership., e = {}".format(user_email, exn))

def attach_gitlab_project_to_user(projectid, user_email, gitlab_host, access_token):
    gl = gitlab.Gitlab(url = "{}/".format(gitlab_host), private_token = access_token)
    project = gl.projects.get(projectid)
    # add user as gitlab project member
    users = gl.users.list(search = user_email)
    try:
        if len(users) == 0:
            log_msg("WARN", "[gitlab][attach_gitlab_project_to_user] Gitlab user {} not found, creating a new user".format(user_email))
            create_gitlab_user(user_email)
            users = gl.users.list(search = user_email)
        log_msg("INFO", "[gitlab][attach_gitlab_project_to_user] gitlab_user_id = {}".format(users[0].id))
        project.members.create({'user_id': users[0].id, 'access_level': gitlab.const.MAINTAINER_ACCESS})
    except Exception as exn:
        log_msg("WARN", "[gitlab][attach_gitlab_project_to_user] Gitlab user {} is already a member of this project due to a greater inherited membership., e = {}".format(user_email, exn))

def get_user_project_by_url(project_url, userid, db):
    from entities.Project import Project
    gitlab_project = Project.getUserProjectByUrl(project_url, userid, db)
    return gitlab_project

def get_user_project_by_name(project_name, userid, db):
    from entities.Project import Project
    gitlab_project = Project.getUserProjectByName(project_name, userid, db)
    return gitlab_project

def get_user_project_by_id(projectid, userid, db):
    from entities.Project import Project
    return Project.getUserProject(projectid, userid, db)

def create_project_access_token(project_id, project_name, gitlab_host, access_token):
    if is_disabled(gitlab_host):
        return None

    expires_at = datetime.now().date() + timedelta(days = 365)

    json_data = {
        "name": f"{project_name}_token",
        "scopes": ["api", "read_api", "read_repository", "write_repository"],
        "expires_at": expires_at.strftime('%Y-%m-%d')
    }
    access_token_response = requests.post(
                                        f'{gitlab_host}/api/v4/projects/{project_id}/access_tokens',
                                        json=json_data,
                                        headers={"PRIVATE-TOKEN": access_token},
                                        timeout=timeout_value
                                    )
    project_access_token = access_token_response.json()
    log_msg("DEBUG", "[gitlab][create_project_access_token] access token body response = {}".format(project_access_token))
    return project_access_token['token']

def get_gitlab_project(project_id, gitlab_host, access_token):
    if is_disabled(gitlab_host) or is_disabled(access_token):
        return {'id': project_id}

    projectReponse = requests.get(f'{gitlab_host}/api/v4/projects/{project_id}', headers={"PRIVATE-TOKEN": access_token}, timeout=timeout_value)
    if projectReponse.status_code == 404:
        log_msg("WARN", "[get_gitlab_project] project not found, project id: {}".format(project_id))
        raise HTTPError("project_not_found_with_gitlab", 404, "project not found", hdrs = {"i18n_code": "project_not_found_with_gitlab"}, fp = None)
    elif projectReponse.status_code == 401:
       log_msg("ERROR", "[get_gitlab_project] unauthorized, project id: {}".format(project_id))
       raise HTTPError("gitlab_unauthorized", 401, "gitlab unauthorized", hdrs = {"i18n_code": "gitlab_unauthorized"}, fp = None)
    project = projectReponse.json()
    log_msg("DEBUG", "[get_gitlab_project] found project: id = {}, payload = {}".format(project_id, project))
    return project

def get_gitlab_project_object(gitlab_url, private_token, project_id):
    gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
    return gl.projects.get(project_id)

def is_not_project_found_in_gitlab(gitlab_project):
    return is_empty(gitlab_project) or 'id' not in gitlab_project or is_empty(gitlab_project['id'])

def get_project_quietly(exist_project):
    if is_empty(exist_project) or is_empty(exist_project.id):
        return None

    gitlab_project = None
    try:
        gitlab_project = get_gitlab_project(exist_project.id, exist_project.gitlab_host, exist_project.access_token)
    except HTTPError as he:
        return {
            "http_code": he.getcode,
            "i18n_code": he.geturl
        }

    return gitlab_project

def get_gitlab_project_tree(project_id, gitlab_host, access_token):
    if is_disabled(gitlab_host) or is_disabled(access_token):
        return []

    projectTreeReponse = requests.get(f'{gitlab_host}/api/v4/projects/{project_id}/repository/tree', headers={"PRIVATE-TOKEN": access_token}, timeout=timeout_value)
    if projectTreeReponse.status_code == 404:
        return []

    project_tree = projectTreeReponse.json()
    return project_tree

def get_gitlab_project_playbooks(project_id, gitlab_host, access_token):
    gitlab_project_tree = get_gitlab_project_tree(project_id, gitlab_host, access_token)
    playbooks = [file for file in gitlab_project_tree if safe_compare_entry(file, "type", "blob") and safe_contain_entry(file, "name", "playbook-")]
    playbooks_names = [playbook['name'].split('.yml')[0] for playbook in playbooks]
    return playbooks_names

def get_gitlab_file_content(project_id, instance_name, gitlab_host, access_token):
    if is_disabled(gitlab_host) or is_disabled(access_token):
        return []

    fileResponse = requests.get(
                            f'{gitlab_host}/api/v4/projects/{project_id}/repository/files/playbook-{instance_name}.yml/blame?ref=main',
                            headers={"PRIVATE-TOKEN": access_token},
                            timeout=timeout_value
                        )
    if fileResponse.status_code == 404:
        raise HTTPError("project_not_found_with_gitlab", 404, "project not found", hdrs = {"i18n_code": "project_not_found_with_gitlab"}, fp = None)
    fileJson = fileResponse.json()
    fileLines = fileJson[0]['lines']
    return fileLines

def get_roles_from_playbook(project_id, instance_name, gitlab_host, access_token):
    file_content_lines = get_gitlab_file_content(project_id, instance_name, gitlab_host, access_token)
    try:
        while True:
            file_content_lines.remove('')
    except ValueError:
        pass

    rolesIndex = file_content_lines.index('  roles:')
    roles = []
    for i in range(rolesIndex+1, len(file_content_lines)-1):
        roles.append(file_content_lines[i].strip().split('- ')[1])

    return roles

def verify_gitlab_host(host):
    if not host:
        return False
    res = requests.get(f'{host}/health', timeout=timeout_value)
    if res.status_code!= 200:
        raise HTTPError("1120", 400, "gitlab host not available", hdrs = {"i18n_code": "1120"}, fp = None)

    return True

def create_gitlab_project(project_name, userid, user_email, host, git_username, access_token, namespace_id, project_type, db):
    default_namespace_id = os.getenv('DYNAMIC_REPO_GROUPID')

    from entities.Project import Project
    namespace = namespace_id if namespace_id else default_namespace_id
    token = access_token if access_token else GIT_DEFAULT_TOKEN
    gitlab_host = host if verify_gitlab_host(host) else GITLAB_URL
    gitUsername = git_username if git_username else GIT_USERNAME

    check_gitlab_url(gitlab_host)
    if is_disabled(GIT_DEFAULT_TOKEN) or is_disabled(default_namespace_id):
        random_id = secrets.randbelow(999) + 1  #? Generate number between 1 and 1000
        project = Project()
        project.id = random_id
        project.name = project_name
        project.url = "{}/{}".format(gitlab_host, project_name)
        project.git_username = gitUsername
        project.access_token = token
        project.gitlab_host = gitlab_host
        project.namespace_id = namespace
        project.userid = userid
        project.type = project_type
        project.save(db)
        return project

    data = {
        "name": project_name,
        "path": project_name,
        "namespace_id": namespace
    }

    projectReponse = requests.post(f'{gitlab_host}/api/v4/projects', json=data, headers={"PRIVATE-TOKEN": token}, timeout=timeout_value)
    if projectReponse.status_code == 400:
        raise HTTPError("project_already_exists_gitlab", 400, "project already exists", hdrs = {"i18n_code": "project_already_exists_gitlab"}, fp = None)
    elif projectReponse.status_code != 201:
        raise HTTPError("creation_project_error_with_gitlab", 400, "a problem accured when creating the project, check your access token", hdrs = {"i18n_code": "creation_project_error_with_gitlab"}, fp = None)
    projectJson = projectReponse.json()

    if gitlab_host == GITLAB_URL and not gitlab_host in get_public_instances():
        log_msg("DEBUG", "[gitlab][create_gitlab_project] attach_gitlab_project_to_user : {}".format(user_email))
        attach_gitlab_project_to_user(projectJson['id'], user_email, gitlab_host, token)
        token = create_project_access_token(projectJson['id'], projectJson['name'], gitlab_host, token)

    project = Project()
    project.id = projectJson['id']
    project.name = projectJson['name']
    project.url = projectJson['http_url_to_repo']
    project.git_username = gitUsername
    project.access_token = token
    project.gitlab_host = gitlab_host
    project.namespace_id = namespace
    project.userid = userid
    project.type = project_type
    project.save(db)
    return project

def get_infra_playbook_roles():
    check_gitlab_url(GITLAB_URL)
    playbook_project_id = os.getenv('PLAYBOOK_REPO_PROJECTID')
    gitlab_connexion_error = JSONResponse(content={
        "status": "ko",
        "message": "can not get roles from gitlab",
        "i18n_code": "can_not_get_roles"
    }, status_code=400)
        
    if is_disabled(playbook_project_id) or is_disabled(GIT_DEFAULT_TOKEN):
        return gitlab_connexion_error, []

    rolesResponse = requests.get(f'{GITLAB_URL}/api/v4/projects/{playbook_project_id}/repository/tree?path=roles&per_page=200&ref=main', headers={"PRIVATE-TOKEN": GIT_DEFAULT_TOKEN}, timeout=timeout_value)
    if not is_response_ok(rolesResponse.status_code):
        log_msg("DEBUG", "[get_infra_playbook_roles] can not get roles from gitlab with url = {}, status = {}".format(GITLAB_URL, rolesResponse.status_code))
        return gitlab_connexion_error, []
    try:
        roles = rolesResponse.json()
        return None, roles
    except ValueError:
        return gitlab_connexion_error, []

def get_project_runners(project_id, gitlab_host, access_token):
    check_gitlab_url(gitlab_host)
    if is_disabled(gitlab_host) or is_disabled(access_token):
        return {}

    runnersResponse = requests.get(f'{gitlab_host}/api/v4/projects/{project_id}/runners', headers={"PRIVATE-TOKEN": access_token}, timeout=timeout_value)
    if runnersResponse.status_code == 404:
        raise HTTPError("project_not_found_with_gitlab", 404, "project not found", hdrs = {"i18n_code": "project_not_found_with_gitlab"}, fp = None)

    runnersJson = runnersResponse.json()
    return runnersJson

def delete_runner(runnerId, gitlab_host, access_token):
    check_gitlab_url(gitlab_host)
    if is_disabled(gitlab_host) or is_disabled(access_token):
        return

    deleteResponse = requests.delete(f'{gitlab_host}/api/v4/runners/{runnerId}', headers={"PRIVATE-TOKEN": access_token}, timeout=timeout_value)
    if deleteResponse.status_code == 404:
        raise HTTPError("runner_not_found", 400, "runner not found", hdrs = {"i18n_code": "runner_not_found"}, fp = None)

def delete_project_runners(project_id, gitlab_host, access_token):
    check_gitlab_url(gitlab_host)
    if is_disabled(gitlab_host) or is_disabled(access_token):
        return

    runners = get_project_runners(project_id, gitlab_host, access_token)
    for runner in runners:
        if exists_entry(runner, "id"):
            delete_runner(runner['id'], gitlab_host, access_token)

def delete_gitlab_project(project_id, gitlab_host, access_token):
    check_gitlab_url(gitlab_host)
    if is_disabled(access_token) or is_disabled(GIT_DEFAULT_TOKEN):
        return

    try:
        delete_project_runners(project_id, gitlab_host, access_token)
    except HTTPError as he:
        log_msg("WARN", "[delete_gitlab_project] something went wrong when deleting project's runners: he = {}".format(he))

    token = GIT_DEFAULT_TOKEN if GITLAB_URL == gitlab_host else access_token
    res = requests.delete(f'{gitlab_host}/api/v4/projects/{project_id}', headers={"PRIVATE-TOKEN": token}, timeout=timeout_value)
    if res.status_code != 202:
        log_msg("WARN", "[delete_gitlab_project] something went wrong when deleting project: status = {}".format(res.status_code))

def read_file_from_gitlab(project_id, file_path, branch, access_token, host):
    gitlab_instance = gitlab.Gitlab(host, private_token=access_token)
    project = gitlab_instance.projects.get(project_id)
    file = project.files.get(file_path, ref=branch)
    file_content = file.decode()
    return file_content

def push_file_to_repository(file_content, file_path, gitlab_connection: gitlab.Gitlab, git_repo_id: str, branch, commit_message):
    fetchedProject = gitlab_connection.projects.get(git_repo_id)
    try:
        fetchedProject.commits.create({
            'branch': branch,
            'commit_message': commit_message,
            'actions': [
                {
                    'action': 'create',
                    'file_path': file_path,
                    'content': base64.b64encode(file_content).decode(),
                    'encoding': 'base64',
                }
            ],
        })
    except gitlab.GitlabCreateError:
        fetchedProject.commits.create({
            'branch': branch,
            'commit_message': commit_message,
            'actions': [
                {
                    'action': 'update',
                    'file_path': file_path,
                    'content': base64.b64encode(file_content).decode(),
                    'encoding': 'base64',
                }
            ],
        })
def push_files_to_repository(files: list[dict], gitlab_connection: gitlab.Gitlab, git_repo_id: str, branch, commit_message):
    fetchedProject = gitlab_connection.projects.get(git_repo_id)
    actions = []
    for file in files:
        file_exists = True
        try:
            fetchedProject.files.get(file_path=file['path'][1:], ref=branch)
        except gitlab.exceptions.GitlabGetError:
            file_exists = False
        
        action = {
            "action": "update" if file_exists else "create",
            "file_path": file["path"],
            'content': file["content"],
        }
        
        actions.append(action)

    try:
        fetchedProject.commits.create({
            'branch': branch,
            'commit_message': commit_message,
            'actions': actions
        })
    except gitlab.GitlabCreateError as e:
        log_msg("WARN", "[push_to_gitlab] error = {}".format(e))
    
def remove_file_from_gitlab(project_id, file_path, commit_message, access_token, host, branch):
    gitlab_instance = gitlab.Gitlab(host, private_token=access_token)
    project = gitlab_instance.projects.get(project_id)
    file = project.files.get(file_path, ref=branch)
    file.delete(branch=branch, commit_message=commit_message)

def init_repository(gitlab_connection: gitlab.Gitlab, git_repo_id: str, branch: str, commit_message: str, readme_content: str):
    fetchedProject = gitlab_connection.projects.get(git_repo_id)
    commits = fetchedProject.commits.list(all=True)
    if not commits:
        fetchedProject.commits.create({
            'branch': branch,
            'commit_message': commit_message,
            'actions': [
                {
                    'action': 'create',
                    'file_path': 'README.md',
                    'content': readme_content,
                }
            ],
        })

def remove_folder_from_gitlab(project_id, folder_path, commit_message, access_token, host, branch):
    try:
        project = get_gitlab_project_object(host, access_token, project_id)
        files_in_folder = project.repository_tree(path=folder_path, ref=branch)

        for file_entry in files_in_folder:
            file_path = file_entry.get('path', '')
            file_type = file_entry.get('type', '')

            if file_type == 'blob':
                file = project.files.get(file_path, ref=branch)
                file.delete(branch=branch, commit_message=commit_message)
            elif file_type == 'tree':
                remove_folder_from_gitlab(project_id, file_path, commit_message, access_token, host, branch)

    except gitlab.GitlabError as e:
        log_msg("WARN", "[delete_gitlab_folder] error = {}".format(e))
        
def get_helm_charts():
    check_gitlab_url(GITLAB_URL)
    charts_project_id = os.getenv('GIT_HELMCHARTS_REPO_ID')
    git_charts_url = os.getenv('GIT_HELMCHARTS_REPO_URL')
    gitlab_connexion_error = JSONResponse(content={
        "status": "ko",
        "message": "can not get helm charts from gitlab",
        "i18n_code": "can_not_get_helm_charts"
    }, status_code=400)
    if is_disabled(charts_project_id) or is_disabled(GIT_DEFAULT_TOKEN):
        return gitlab_connexion_error, []
    parsed_url = urlparse(f'{git_charts_url}')
    host = f"{parsed_url.scheme}://{parsed_url.netloc}"
    charts_response = requests.get(
        f'{host}/api/v4/projects/{charts_project_id}/repository/tree?path=charts&per_page=200&ref=main', 
        headers={"PRIVATE-TOKEN": GIT_DEFAULT_TOKEN},
        timeout=timeout_value
    )
    if not is_response_ok(charts_response.status_code):
        log_msg("DEBUG", "[get_helm_charts] can not get helm charts from gitlab with url = {}, status = {}".format(host, charts_response.status_code))
        return gitlab_connexion_error, []
    try:
        charts = charts_response.json()
        return None, charts
    except ValueError:
        return gitlab_connexion_error, []


def push_selected_chart(charts:list[str], gitlab_connection: gitlab.Gitlab, git_repo_id: str):
    fetchedProject = gitlab_connection.projects.get(git_repo_id)
    fetchedProject.commits.create({
        'branch': 'main',
        'commit_message': 'init charts',
        'actions': [{
            "action": "create",
            "content": file["content"],
            "file_path": file["path"]
        } for file in charts]
    })
