import os
import shutil
import gitlab

from typing import Optional

from pathlib import Path
from git import Repo

from fastapi.responses import JSONResponse
from jinja2 import Environment, FileSystemLoader

from schemas.Kubernetes import ExternalChart
from utils.common import is_not_empty
from utils.gitlab import push_files_to_repository
from utils.observability.cid import get_current_cid

access_token = os.getenv('GIT_PRIVATE_TOKEN')
git_username = os.getenv('GIT_USERNAME')
repo_dir = os.getenv('LOCAL_CLONE_CHARTS_URL')
charts_url = os.getenv('GIT_HELMCHARTS_REPO_URL')

def push_charts(project_id, gitlab_host, token,charts:list[str]):
    if None in (access_token, git_username, repo_dir, charts_url):
        raise ValueError("One or more required environment variables are missing.")

    # Repository to clone
    git_url = f'https://{git_username}:{access_token}@{charts_url}'
    root_dir = f'{repo_dir}_{project_id}'
    
    try:
        Repo.clone_from(git_url, root_dir, branch='main')
        charts_files = []
        gitlab_connection = gitlab.Gitlab(url = gitlab_host, private_token=token)

        path_tpl = "{}/{}"
        charts_path = "{}/charts".format(root_dir)

        # delete uncecessary charts
        for dir in os.listdir(charts_path):
            if dir not in charts:
                shutil.rmtree(path_tpl.format(charts_path, dir))

        for root, dirs, files in os.walk(charts_path):
            new_root = root.replace(root_dir, "")
            if is_not_empty(files):
                for file in files:
                    root.replace(root_dir, "")
                    charts_files.append({
                        "path": path_tpl.format(new_root, file),
                        "content": open(path_tpl.format(root, file), 'r').read()
                    })

        push_files_to_repository(charts_files, gitlab_connection, project_id, 'main', 'Added Manifest')
        shutil.rmtree(root_dir)
    except Exception as e:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'error pushing charts',
            'cid': get_current_cid()
        }, status_code = 500)

    return JSONResponse(content = {
        'status': 'ok',
        'message': 'charts pushed'
    }, status_code = 200)

def generate_chart_yaml(charts:list[str], external_charts:Optional[list[ExternalChart]] = None):
    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[2]) + '/templates/kubernetes/app')
    env = Environment(loader = file_loader)
    template = env.get_template('Chart.yaml.j2')
    chart_yaml = template.render(
        dependencies = charts,
        external_dependencies = external_charts
    )

    return chart_yaml
