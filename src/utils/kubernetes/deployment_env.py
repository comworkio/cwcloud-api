import os
import shutil
from pathlib import Path
from typing import Optional

import gitlab
import yaml
from fastapi.responses import JSONResponse
from git import Repo
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

from schemas.Kubernetes import ExternalChart
from utils.gitlab import push_files_to_repository
from utils.observability.cid import get_current_cid
from utils.common import AUTOESCAPE_EXTENSIONS

access_token = os.getenv('GIT_PRIVATE_TOKEN')
git_username = os.getenv('GIT_USERNAME')
repo_dir = os.getenv('LOCAL_CLONE_CHARTS_URL')
charts_url = os.getenv('GIT_HELMCHARTS_REPO_URL')

git_url = f'https://{git_username}:{access_token}@{charts_url.replace("https://", "")}'

def push_charts(
    project_id,
    gitlab_host,
    deployment_name: str,
    namespace: str,
    values: str,
    readme: str,
    token: str,
    charts: list[str],
    external_charts: Optional[list[ExternalChart]],
    args: Optional[dict[str, any]],
):
    if None in (access_token, git_username, repo_dir, charts_url):
        raise ValueError(
            "One or more required environment variables are missing.")

    file_loader = FileSystemLoader(
        str(Path(__file__).resolve().parents[2]) + "/templates/kubernetes/app"
    )
    env = Environment(loader=file_loader, autoescape=select_autoescape(AUTOESCAPE_EXTENSIONS))
    template = env.get_template("Chart.yaml.j2")
    doc_template = Template(readme)
    value_template = Template(values)
    root_dir = f"{repo_dir}_{project_id}"

    try:
        charts_files = []
        gitlab_connection = gitlab.Gitlab(url=gitlab_host, private_token=token)

        path_tpl = "{}/{}"
        root_dir = f"{repo_dir}_{project_id}"
        charts_path = "{}/charts".format(root_dir)
        clone_chart_repo(git_url, root_dir, charts_path, charts)

        for root, dirs, files in os.walk(charts_path):
            new_root = root.replace(root_dir, "")
            if "external-chart.yaml" not in files:
                for file in files:
                    root.replace(root_dir, "")
                    charts_files.append(
                        {
                            "path": path_tpl.format(new_root, file),
                            "content": open(path_tpl.format(root, file), "r").read(),
                        }
                    )
            else:
                get_external_dependency_data(root, external_charts, charts)

        charts_files.extend([
            {
                "path": "/Chart.yaml",
                "content": template.render(
                    name=deployment_name,
                    dependencies=charts,
                    external_dependencies=external_charts,
                ),
            },
            {
                "path": "/values.yaml",
                "content": value_template.render(args=args),
            },
            {
                "path": "/README.md",
                "content": doc_template.render(
                    name=namespace,
                    deployment_name=deployment_name,
                    dependencies=charts,
                    external_dependencies=external_charts,
                    args=args,
                ),
            }]
        )
        push_files_to_repository(
            charts_files, gitlab_connection, project_id, "main", "Added Manifest"
        )
        shutil.rmtree(root_dir)
    except Exception as e:
        return JSONResponse(
            content={
                "status": "ko",
                "message": "error pushing charts",
                "cid": get_current_cid(),
            },
            status_code=500,
        )

    return JSONResponse(
        content={"status": "ok", "message": "charts pushed"}, status_code=200
    )



def get_external_dependency_data(root: str, external_charts: list[ExternalChart], charts: list[str]):
    with open(f"{root}/external-chart.yaml", 'r') as yaml_file:
        external_chart_file = yaml.safe_load(yaml_file)
        new_chart = ExternalChart(
            name=external_chart_file["name"],
            version=external_chart_file["version"],
            repository=external_chart_file["repository"]
        )
        external_charts.append(new_chart)
        dependency = root.split("/")[-1]
        if dependency in charts:
            charts.remove(dependency)
        
def clone_chart_repo(git_url, root_dir, charts_path,charts):
    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)
        
    Repo.clone_from(git_url, root_dir, branch='main')

    path_tpl = "{}/{}"
    for dir in os.listdir(charts_path):
        if dir not in charts:
            shutil.rmtree(path_tpl.format(charts_path, dir))