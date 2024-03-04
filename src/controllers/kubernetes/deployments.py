import yaml
import json
import gitlab

from pathlib import Path

from fastapi.responses import JSONResponse
from kubernetes import config, client
from urllib3.exceptions import MaxRetryError

from entities.kubernetes.Deployment import Deployment
from entities.Environment import Environment
from entities.kubernetes.Cluster import Cluster
from entities.Project import Project
from schemas.User import UserSchema
from schemas.Kubernetes import DeploymentSchema

from utils.common import is_not_empty, is_true
from utils.encoder import AlchemyEncoder
from utils.gitlab import  push_files_to_repository
from utils.kubernetes.deployment_env import push_charts
from utils.kubernetes.k8s_management import set_git_config,delete_custom_resource
from utils.bytes_generator import generate_random_bytes

GROUP = "helm.toolkit.fluxcd.io"
VERSION = "v2beta2"
PLURAL = "helmreleases"
NAMESPACE = "flux-system"

def get_deployments(current_user: UserSchema, db):
    if current_user.is_admin:
        deployments = Deployment.getAll(db)
    else:
        deployments = Deployment.getAllByUser(current_user.id, db)

    deploymentJson = json.loads(json.dumps(deployments, cls = AlchemyEncoder))
    
    deploymentJson = [{
        **deployment,
        "namespace": f'{deployment["name"]}-{deployment["hash"]}',
    } for deployment in deploymentJson]
    
    return JSONResponse(content = deploymentJson, status_code = 200)

def create_new_deployment(current_user:UserSchema,deployment:DeploymentSchema, db):
    env: Environment = Environment.getById(deployment.env_id, db)

    if not env and not env.type == "vm":
        return JSONResponse(content = {"message": "environment not found", "i18n_code": "1504"}, status_code = 404)

    project = Project.getById(deployment.project_id, db)
    
    if not project:
        return JSONResponse(content = {"message": "project not found", "i18n_code": "803"}, status_code = 404)
    
    deployments = Deployment.getAllByProject(project.id, db)
    if is_not_empty(deployments) > 0 and deployments[0].env_id != deployment.env_id:
        return JSONResponse(content = {"message": "can't select a different environment for this project", "i18n_code": "1606"}, status_code = 400)
    
    cluster = Cluster.getById(deployment.cluster_id, db)
    if not cluster:
        return JSONResponse(content = {"message": "cluster not found", "i18n_code": "1404"}, status_code = 404)
    
    push_charts(project.id, project.gitlab_host, project.access_token, env.roles.split(";"))

    path = str(Path(__file__).resolve().parents[2]) + '/constants/k8s_app_readme.md'
    with open(path, 'r') as file:
        readme_content = file.read()

    files = [{"path": "Chart.yaml","content": env.environment_template},{ "path": "README.md", "content": readme_content}]

    gitlab_connection = gitlab.Gitlab(url = project.gitlab_host, private_token=project.access_token)
    push_files_to_repository(files, gitlab_connection, project.id, 'main', 'Added Chart file')
    generatedHash = generate_random_bytes(6)
    deployment.name = deployment.name.lower()
    kubeconfigFile = cluster.getKuberConfigFileByClusterId(cluster.id, db)
    generatedName = f'{deployment.name}-{generatedHash}'
    set_git_config(kubeconfigFile.content,generatedName,generatedName,project)
    deployment = Deployment(name=deployment.name,
                            description=deployment.description,
                            cluster_id = deployment.cluster_id,
                            project_id = deployment.project_id,
                            env_id = deployment.env_id,
                            hash=generatedHash,
                            user_id=current_user.id)
    deployment.save(db)
    deploymentJson = json.loads(json.dumps(deployment, cls = AlchemyEncoder))
    return JSONResponse(content = deploymentJson,status_code = 201)

def get_deployment(current_user:UserSchema,deployment_id:int, db):
    deployment = Deployment.findOne(deployment_id, db)
    if not deployment:
        return JSONResponse(content = {"message": "deployment not found", "i18n_code": "1604"}, status_code = 404)

    if deployment.user_id != current_user.id and not current_user.is_admin:
        return JSONResponse(content = {"message": "you dont have permission to get this deployment", "i18n_code": "1603"}, status_code = 403)
    
    kubeConfig = Cluster.getKuberConfigFileByClusterId(deployment.cluster_id, db)
    config_file = yaml.safe_load(kubeConfig.content)
    config.load_kube_config_from_dict(config_file)
    v1 = client.CoreV1Api()
    
    try:
        pods = v1.list_namespaced_pod(f'{deployment.name}-{deployment.hash}').items
    except MaxRetryError:
        return JSONResponse(content = {"message": "couldn't connect to the cluster", "i18n_code": "1401"}, status_code = 500)
    
    project = Project.getById(deployment.project_id, db)
    env = Environment.getById(deployment.env_id, db)
    
    containers = []
    podsData = [] 
    for pod in pods:
        podsData.append({
            "id": pod.metadata.name + deployment.name,
            "name": pod.metadata.name,
            "status": pod.status.phase,
            "ip": pod.status.pod_ip,
            "start_time": pod.status.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
        })
    
        for container in zip(pod.spec.containers,pod.status.container_statuses):
            if container[1].state.waiting:
                podsData[-1]["status"] = container[1].state.waiting.reason
            containers.append({
                "id": container[0].name + pod.metadata.name,
                "name": container[0].name,
                "image": container[0].image,
                "started": container[1].started,
                "restart_count": container[1].restart_count,
                "state": {
                    "running": True if container[1].state.running else False,
                    "terminated": True if container[1].state.terminated else False,
                    "waiting": True if container[1].state.waiting else False,
                },
            })

    return JSONResponse(content = {
            "name": deployment.name,
            "namespace": f'{deployment.name}-{deployment.hash}',
            "pods": podsData,
            "containers": containers ,
            "project": {
                "id": deployment.project_id,
                "name": project.name,
            },
            "environment": {
                "id": deployment.env_id,
                "name": env.name,
            }
        }, status_code = 200)

def delete_deployment(current_user:UserSchema,deployment_id:int, db):
    deployment = Deployment.findOne(deployment_id, db)
    if not deployment:
        return JSONResponse(content = {"message": "deployment not found", "i18n_code": "1604"}, status_code = 404)

    if deployment.user_id != current_user.id and not current_user.is_admin:
        return JSONResponse(content = {"message": "you dont have permission to delete this deployment", "i18n_code": "1603"}, status_code = 403)
    
    cluster = Cluster.getById(deployment.cluster_id, db)
    kubeconfigFile = cluster.getKuberConfigFileByClusterId(cluster.id, db)
    deleted = delete_custom_resource(GROUP, VERSION, PLURAL, f'{deployment.name}-{deployment.hash}-release', NAMESPACE, kubeconfigFile.content)
    config.load_kube_config_from_dict(yaml.safe_load(kubeconfigFile.content))
    v1 = client.CoreV1Api()
    v1.delete_namespace(f'{deployment.name}-{deployment.hash}')

    if is_true(deleted):
        deployment.delete(db)
        return JSONResponse(content = {"message": "deployment deleted"}, status_code = 200)
    else:
        return JSONResponse(content = {"message": "couldn't delete deployment from the cluster", "i18n_code": "1605"}, status_code = 500)
