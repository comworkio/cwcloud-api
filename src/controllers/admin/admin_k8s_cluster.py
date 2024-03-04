from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import UploadFile
from kubernetes import client, config

from schemas.User import UserSchema
from entities.kubernetes.Cluster import Cluster
from entities.kubernetes.KubeconfigFile import KubeConfigFile

from utils.yaml import read_uploaded_yaml_file
from utils.yaml import read_uploaded_yaml_file
from utils.kubernetes.k8s_management import get_dumped_json, install_flux

def get_all_clusters(db):
    clusters = Cluster.getAll(db) 
    response = get_dumped_json(clusters)
    return JSONResponse(content = response, status_code = 200)

def get_cluster_by_user(current_user, cluster_id, db):
    cluster = Cluster.findOneByUser(cluster_id, current_user.id, db)
    if not cluster:
        return JSONResponse(content = {"error": "cluster not found", "i18n_code": "404"}, status_code = 404)

    return cluster

def get_clusters_byKubeconfigFile(current_user, kubeconfig_file_id, db):
    clusters = Cluster.findByKubeConfigFileAndUserId(kubeconfig_file_id, current_user.id, db)
    if not clusters:
        return JSONResponse(content = {"error": "clusters not found", "i18n_code": "404"}, status_code = 404)

    dumpedClusters = get_dumped_json(clusters)
    return JSONResponse(content = dumpedClusters, status_code = 200)

def get_cluster_infos(current_user, cluster_id, db):
    cluster = get_cluster_by_user(current_user, cluster_id, db)
    kubeconfigFile = KubeConfigFile.findOne(cluster.kubeconfig_file_id, db)
    kc_content = read_uploaded_yaml_file(kubeconfigFile.content)
    
    config.load_kube_config_from_dict(kc_content)
    core_v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()
    v1Server = client.VersionApi()
    custom_obj = client.CustomObjectsApi()

    # Get the server info
    server_version = v1Server.get_code()
    pods = core_v1.list_pod_for_all_namespaces(watch=False)
    nodes = core_v1.list_node()
    node_metrics = custom_obj.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
    
    # Get the max pods capacity of the cluster
    max_pods = 0
    nodes_result = []
    for i in range(len(nodes.items)):
        node = nodes.items[i]
        node_metric = node_metrics['items'][i]['usage']
        
        max_pods += int(node.status.allocatable["pods"])
        nodes_result += [{
            "name": node.metadata.name, 
            "ip": node.status.addresses[0].address, 
            "status": node.status.conditions[3].type,
            "t_cpu":node.status.capacity["cpu"],
            "t_memory":node.status.capacity["memory"],
            "u_cpu":node_metric['cpu'],
            "u_memory":node_metric['memory']
        }]
    
    node_metrics = custom_obj.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")

    pods_result =  [
        {
            "name": pod.metadata.name, 
            "namespace": pod.metadata.namespace, 
            "ip": pod.status.pod_ip , 
            "status": pod.status.phase , 
        } for pod in pods.items
    ]

    deployments_result = [
        {
            "name": deployment.metadata.name,
            "namespace": deployment.metadata.namespace,
            "replicas": deployment.status.replicas,
            "available_replicas": deployment.status.available_replicas,
            "ready_replicas": deployment.status.ready_replicas,
            "updated_replicas": deployment.status.updated_replicas,
            "age": deployment.metadata.creation_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')
        } for deployment in apps_v1.list_deployment_for_all_namespaces().items
    ]
    
    namespaces = core_v1.list_namespace().items

    return JSONResponse(content = {
        "server_info":{"version": server_version.git_version, "platform": server_version.platform,},
        "pods":pods_result,"nodes":nodes_result,"max_pods":max_pods,"total_namespaces":len(namespaces), 
        "deployments": deployments_result}, status_code = 200)

def get_cluster_byKubeconfigFile(kubeconfig_file_id, db):
    clusters = Cluster.findByKubeConfigFile(kubeconfig_file_id.id, db)
    dumpedClusters = get_dumped_json(clusters)
    return JSONResponse(content = dumpedClusters, status_code = 200)

def save_kubeconfig(current_user:UserSchema, kubeconfig:UploadFile, db:Session):
    file = kubeconfig.file.read()
    
    kubeconfigFile = KubeConfigFile(content = file , owner_id = current_user.id)
    kubeconfigFile.save(db)
    
    try:
        read_clusters_and_save(file, kubeconfigFile.id, db)
    except Exception:
        kubeconfigFile.delete(db)
        return JSONResponse(content = {"error": "please verify the kubeconfig file", "i18n_code": "1400"}, status_code = 400)
    
    kubeconfig.file.close()
    return JSONResponse(content = {"message": "kubeconfig successfully uploaded","file_id":kubeconfigFile.id}, status_code = 200)

def read_clusters_and_save(file, file_id, db):
    kc_content = read_uploaded_yaml_file(file)
    
    config.load_kube_config_from_dict(kc_content)
    v1Server = client.VersionApi()
    server_version = v1Server.get_code()
    
    for cluster in kc_content.get('clusters',[]):
        cl = Cluster()
        cl.name = cluster.get('name')
        cl.kubeconfig_file_id = file_id
        cl.platform = server_version.platform,
        cl.version = server_version.git_version,
        cl.save(db)
        install_flux(file)

def delete_cluster_by_id(current_user, cluster_id, db):
    cluster: Cluster = get_cluster_by_user(current_user,cluster_id,db)
    if cluster is None:
        return JSONResponse(content = {"error": "cluster not found", "i18n_code": "1404"}, status_code = 404)

    Cluster.deleteOne(cluster.id, db)
    return JSONResponse(content = {"message": "Cluster successfully deleted"}, status_code = 200)
