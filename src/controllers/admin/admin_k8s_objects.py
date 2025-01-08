import yaml
import json

from fastapi import UploadFile

from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
from kubernetes import client, config, dynamic
from kubernetes.client.rest import ApiException

from entities.kubernetes.Cluster import Cluster
from entities.kubernetes.KubeconfigFile import KubeConfigFile

from constants.k8s_constants import K8S_OBJECTS, K8S_RESOURCES
from schemas.Kubernetes import ObjectAddSchema, ObjectSchema
from schemas.User import UserSchema

from utils.gitlab import GIT_HELMCHARTS_REPO_ID, GIT_HELMCHARTS_REPO_URL, read_file_from_gitlab, GIT_DEFAULT_TOKEN
from utils.yaml import read_uploaded_yaml_file
from utils.kubernetes.object import generate_object
from utils.kubernetes.object import clear_metadata
from utils.common import convert_dict_keys_to_camel_case, is_empty
from utils.observability.cid import get_current_cid

def get_cluster_configfile(current_user: UserSchema, cluster_id: int, db: Session):
    cluster: Cluster = Cluster.getById(cluster_id, db)
    if not cluster:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Cluster not found', 
            'i18n_code': '2fa_method_not_found',
            'cid': get_current_cid()
        }, status_code = 404)

    kubeconfigFile = KubeConfigFile.findOne(cluster.kubeconfig_file_id,db)
    kc_content = read_uploaded_yaml_file(kubeconfigFile.content)
    return kc_content

def get_cluster_services(current_user: UserSchema, cluster_id: int, db: Session):
    kc_content = get_cluster_configfile(current_user, cluster_id, db)
    
    config.load_kube_config_from_dict(kc_content)
    v1 = client.CoreV1Api()
    services = v1.list_service_for_all_namespaces()
    services_result =  [
        {
            "name": service.metadata.name, 
            "namespace": service.metadata.namespace, 
            "type": service.spec.type,
            "selectors": service.spec.selector,
            "targets": [port.to_dict() for port in service.spec.ports],
            "creation_date": service.metadata.creation_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')
        } for service in services.items
    ]

    return JSONResponse(content = services_result, status_code = 200)

def get_cluster_general_services(current_user: UserSchema, cluster_id: int, db: Session):
    kc_content = get_cluster_configfile(current_user, cluster_id, db)
    
    config.load_kube_config_from_dict(kc_content)
    v1 = client.CoreV1Api()
    services = v1.list_service_for_all_namespaces()
    services_result =  [
        {
            "name": service.metadata.name, 
            "namespace": service.metadata.namespace, 
        } for service in services.items
    ]

    return JSONResponse(content = services_result, status_code = 200)

def get_cluster_general_namespaces(current_user: UserSchema, cluster_id: int, db: Session):
    kc_content = get_cluster_configfile(current_user, cluster_id, db)
    
    config.load_kube_config_from_dict(kc_content)
    v1 = client.CoreV1Api()
    namespaces = v1.list_namespace()
    namespaces_result =  [ namespace.metadata.name for namespace in namespaces.items ]
    return JSONResponse(content = namespaces_result, status_code = 200)

def get_cluster_config_maps(current_user: UserSchema, cluster_id: int, db: Session):
    kc_content = get_cluster_configfile(current_user, cluster_id, db)
    
    config.load_kube_config_from_dict(kc_content)
    v1 = client.CoreV1Api()
    config_maps = v1.list_config_map_for_all_namespaces()
    config_maps_results =  [
        {
            "name": cm.metadata.name, 
            "namespace": cm.metadata.namespace, 
            "data_type": list(cm.data.keys()) if hasattr(cm, 'data') and cm.data else [],
            "creation_date": cm.metadata.creation_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')
        } for cm in config_maps.items
    ]

    return JSONResponse(content = config_maps_results, status_code = 200)

def get_cluster_ingresses(current_user: UserSchema, cluster_id: int, db: Session):
    kc_content = get_cluster_configfile(current_user, cluster_id, db)
    
    config.load_kube_config_from_dict(kc_content)
    v1 = client.NetworkingV1Api()
    ingresses = v1.list_ingress_for_all_namespaces()
    ingress_result =  [
        {
            "name": ingress.metadata.name, 
            "namespace": ingress.metadata.namespace, 
            "creation_date": ingress.metadata.creation_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            "ingressClassName": ingress.spec.ingress_class_name if ingress.spec.ingress_class_name else "",
            "targets": [{
                "host": host.host if host.host else None,
                "target_service": host.http.paths[0].backend.service.name if host.http.paths else None,
                "target_service_port": host.http.paths[0].backend.service.port.number if host.http.paths[0].backend.service.port.number else None,
                "path":  (host.http.paths[0].path if host.http.paths[0].path else "/") if host.http.paths else None,
                "path_type": host.http.paths[0].path_type if host.http.paths[0].path_type else None
            } for host in ingress.spec.rules],
        } for ingress in ingresses.items
    ]
    return JSONResponse(content = ingress_result, status_code = 200)

def get_cluster_secrets(current_user: UserSchema, cluster_id: int, db: Session):
    kc_content = get_cluster_configfile(current_user, cluster_id, db)
    
    config.load_kube_config_from_dict(kc_content)
    v1 = client.CoreV1Api()
    secrets = v1.list_secret_for_all_namespaces()
    secrets_result =  [
        {
            "name": secret.metadata.name, 
            "namespace": secret.metadata.namespace, 
            "creation_date": secret.metadata.creation_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            "type": secret.type,
        } for secret in secrets.items
    ]
    return JSONResponse(content = secrets_result, status_code = 200)

def get_cluster_ingress_classes(current_user: UserSchema, cluster_id: int, db: Session):
    kc_content = get_cluster_configfile(current_user, cluster_id, db)
    
    config.load_kube_config_from_dict(kc_content)
    v1 = client.NetworkingV1Api()
    ingress_classes = v1.list_ingress_class()
    ingress_classes_result =  [
        {
            "name": ic.metadata.name, 
            "controller": ic.spec.controller,
            "parameters": ic.spec.parameters if hasattr(ic.spec, 'parameters') and ic.spec.parameters else [],
            "creation_date": ic.metadata.creation_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')
        } for ic in ingress_classes.items
    ]
    return JSONResponse(content = ingress_classes_result, status_code = 200)

def delete_resource(kc_content, manifest: ObjectSchema, api_group: str, api_version: str, plural: str):
    config.load_kube_config_from_dict(kc_content)
    dynamic_client = dynamic.DynamicClient(
        client.api_client.ApiClient()
    )

    resource = dynamic_client.resources.get(api_version=api_version ,kind=K8S_OBJECTS[manifest.kind.lower()])
    dynamic_client.delete(resource=resource,name=manifest.name, namespace=manifest.namespace, api_version=f"{api_group}/{api_version}")

def delete_object(current_user: UserSchema, object: ObjectSchema, db: Session):
    cluster: Cluster = Cluster.getById(object.cluster_id, db)
    kubeconfigFile: KubeConfigFile = KubeConfigFile.findOne(cluster.kubeconfig_file_id,db)
    kc_content = read_uploaded_yaml_file(kubeconfigFile.content)
    resource = K8S_RESOURCES[object.kind]
    delete_resource(kc_content, object, resource['api_group'], resource['api_version'], resource['plural'])
    return JSONResponse(content = {
        'status': 'ok',
        'message': 'Successfully deleted object'
    }, status_code = 200)

def update_object(current_user: UserSchema, object: ObjectSchema,yaml_file:UploadFile, db: Session):
    cluster: Cluster = Cluster.getById(object.cluster_id, db)
    if not cluster:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'Cluster not found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    kubeconfigFile: KubeConfigFile = KubeConfigFile.findOne(cluster.kubeconfig_file_id,db)
    kc_content = read_uploaded_yaml_file(kubeconfigFile.content)
    file = yaml.safe_load(yaml_file.file.read())
    yaml_file.file.close()
    
    res = apply_resource(kc_content, file, object, True)
    
    return res if res else JSONResponse(content = {
        'status': 'ok',
        'message': 'Successfully updated object'
    }, status_code = 200)

def add_object_to_cluster(current_user:UserSchema, values_file:UploadFile, object:ObjectAddSchema, db:Session):
    # Validate parameters
    cluster: Cluster = Cluster.getById(object.cluster_id, db)
    
    if not cluster:
        return JSONResponse(content = {
            'status': 'ko',
            'error': "Cluster doesn't exist", 
            'i18n_code': 'project_name_missing',
            'cid': get_current_cid()
        }, status_code = 404)
    
    kubeconfig_file: KubeConfigFile = KubeConfigFile.findOne(cluster.kubeconfig_file_id, db)
    if not kubeconfig_file:
        return JSONResponse(content = {
            'status': 'ko',
            'error': "You don't have any project linked with the mentioned id", 
            'i18n_code': 'project_name_missing',
            'cid': get_current_cid()
        }, status_code = 404)
       
    if object.kind not in K8S_OBJECTS:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'object kind is not supported', 
            'i18n_code': 'project_name_missing',
            'cid': get_current_cid()
        }, status_code = 400)
    
    # Extract object required values
    vf_content = read_uploaded_yaml_file(values_file.file)
    file_name = vf_content['name']
    file_namespace = vf_content['namespace']

    if is_empty(file_namespace):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'namespace is required',
            'i18n_code': 'project_name_missing',
            'cid': get_current_cid()
        }, status_code = 400)

    if is_empty(file_name):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'name is required',
            'i18n_code': 'project_name_missing',
            'cid': get_current_cid()
        }, status_code = 400)

    # Generate and apply resource
    output = generate_object(values_file, object)
    rc_info = ObjectSchema(kind=object.kind, cluster_id=object.cluster_id, name=file_name, namespace=file_namespace)
    kubeconfigFile: KubeConfigFile = KubeConfigFile.findOne(cluster.kubeconfig_file_id,db)
    kc_content = read_uploaded_yaml_file(kubeconfigFile.content)
    res = apply_resource(kc_content, yaml.safe_load(output), rc_info)

    return res if res else JSONResponse(content = {
        'status': 'ok',
        'message': 'Manifest successfully added'
    }, status_code = 200)

def get_chart_values(kind):
    host = f'{GIT_HELMCHARTS_REPO_URL.replace("https://","").split("/")[0]}'
    f = read_file_from_gitlab(GIT_HELMCHARTS_REPO_ID, f'objects-management-values/{kind}.yaml','main', GIT_DEFAULT_TOKEN, host)
    return PlainTextResponse(content = f, status_code = 200)

def apply_resource(kc_content, file, manifest: ObjectSchema, isUpdate: bool = False):
    config.load_kube_config_from_dict(kc_content)
    dynamic_client = dynamic.DynamicClient(
        client.ApiClient()
    )

    yaml_namespace = file['metadata']['namespace']
    
    resource_data = K8S_RESOURCES[manifest.kind]
    api_version = resource_data['api_version']
    resource = dynamic_client.resources.get(api_version=api_version ,kind=file['kind'])
    
    try:
        if isUpdate:
            dynamic_client.replace(resource,name=manifest.name, namespace=manifest.namespace,body=file)
        else:
            dynamic_client.create(resource,namespace=yaml_namespace,body=file)
    except ApiException as e:
        b = json.loads(e.body)
        return JSONResponse(content = {
            'status': 'ko',
            'error': b['message'], 
            'i18n_code': 'error_while_create_object',
            'cid': get_current_cid()
        }, status_code = 400)    
    
def get_object(current_user: UserSchema, object: ObjectSchema, db: Session):
    if object.kind not in K8S_OBJECTS:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'object kind is not supported', 
            'i18n_code': 'project_name_missing',
            'cid': get_current_cid()
        }, status_code = 400)

    cluster: Cluster = Cluster.getById(object.cluster_id, db)
    kubeconfigFile: KubeConfigFile = KubeConfigFile.findOne(cluster.kubeconfig_file_id,db)
    kc_content = read_uploaded_yaml_file(kubeconfigFile.content)
    config.load_kube_config_from_dict(kc_content)
    dynamic_client = dynamic.DynamicClient(client.ApiClient())
    try:
        resource = dynamic_client.resources.get(
            api_version=f"{K8S_RESOURCES[object.kind.lower()]['api_version']}",
            kind=K8S_OBJECTS[object.kind.lower()]
        )

        found_object = dynamic_client.get(
            resource=resource,
            name=object.name,
            namespace=object.namespace
        ).to_dict()
    
        clear_metadata(found_object)
        return PlainTextResponse(content = yaml.safe_dump(convert_dict_keys_to_camel_case(found_object)), status_code = 200)
    except ApiException as e:
        b = json.loads(e.body)
        return JSONResponse(content = {
            'status': 'ko',
            'error': b['message'], 
            'i18n_code': 'error_while_create_object',
            'cid': get_current_cid()
        }, status_code = 400)
