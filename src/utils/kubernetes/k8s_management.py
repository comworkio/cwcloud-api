import json
import yaml
import requests
from entities.Project import Project
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from base64 import b64encode
from kubernetes import client, config, dynamic
from constants.k8s_constants import FLUX_FILE_URL
from utils.encoder import AlchemyEncoder

def install_flux(config_file: bytes):
    flux_yaml_file = yaml.safe_load_all(requests.get(FLUX_FILE_URL).content)
    config_file = yaml.safe_load(config_file)
    
    config.load_kube_config_from_dict(config_file)

    DYNAMIC_CLIENT = dynamic.DynamicClient(
        client.api_client.ApiClient()
    )

    apply_items(DYNAMIC_CLIENT, flux_yaml_file)
                
def apply_item(dynamic_client: dynamic.DynamicClient, manifest: dict):
    api_version = manifest.get("apiVersion")
    kind = manifest.get("kind")
    resource_name = manifest.get("metadata").get("name")
    namespace = manifest.get("metadata").get("namespace")
    crd_api = dynamic_client.resources.get(api_version=api_version, kind=kind)

    try:
        crd_api.get(namespace=namespace, name=resource_name)
        crd_api.patch(body=manifest, content_type="application/merge-patch+json")

    except dynamic.exceptions.NotFoundError:
        crd_api.create(body=manifest, namespace=namespace)

def apply_items(dynamic_client: dynamic.DynamicClient, manifests: list):
    for manifest in manifests:
        apply_item(dynamic_client, manifest)

def get_dumped_json(obj):
    return json.loads(json.dumps(obj, cls = AlchemyEncoder, skipkeys=True))

def set_git_config(config_file:bytes, name:str, namespace:str, project:Project):
    config_file = yaml.safe_load(config_file)
    config.load_kube_config_from_dict(config_file)
    dynamic_client = dynamic.DynamicClient(
        client.api_client.ApiClient()
    )

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[2]) + '/templates/kubernetes/fluxgit')
    env = Environment(loader = file_loader)
    template = env.get_template('fluxgit.yaml.j2')

    output = template.render(
        git_username = b64encode(project.git_username.encode("utf-8")).decode("utf-8"), 
        git_password = b64encode(project.access_token.encode("utf-8")).decode("utf-8"),
        git_url = project.url, 
        name = name, 
        namespace = namespace
    )

    apply_items(dynamic_client, yaml.safe_load_all(output))

def delete_custom_resource(group: str, version: str, plural: str, name: str, namespace: str, config_file: bytes):
    try:
        config.load_kube_config_from_dict(yaml.safe_load(config_file))
        api = client.CustomObjectsApi()
        api.delete_namespaced_custom_object(group, version, namespace, plural, name)
        return True

    except client.exceptions.ApiException as e:
        if 'not found' in e.reason.lower():
            return True

    except Exception as e:
        return False
