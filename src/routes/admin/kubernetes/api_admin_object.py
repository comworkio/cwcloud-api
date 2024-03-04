import json
from pydantic import Json
from typing import Literal
from controllers.admin.admin_k8s_objects import add_object_to_cluster, delete_object, get_cluster_config_maps,get_object, get_cluster_services, get_cluster_ingresses ,update_object,get_chart_values,get_cluster_secrets,get_cluster_general_services,get_cluster_general_namespaces, get_cluster_ingress_classes
from database.postgres_db import get_db
from schemas.Kubernetes import ObjectAddSchema, ObjectSchema
from sqlalchemy.orm import Session
from fastapi import APIRouter, Form, UploadFile, File, Depends
from typing import Annotated
from schemas.User import UserSchema
from middleware.auth_guard import admin_required
from middleware.k8sapi_guard import k8sapi_required


router = APIRouter()

# Get k8s objects from cluster
@router.get("/cluster/{cluster_id}/services")
def get_services(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    return get_cluster_services(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/configMaps")
def get_config_maps(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    return get_cluster_config_maps(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/ingresses")
def get_ingresses(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    return get_cluster_ingresses(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/secrets")
def get_secrets(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    return get_cluster_secrets(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/general/services")
def get_general_services(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    return get_cluster_general_services(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/general/namespaces")
def get_general_namespaces(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    return get_cluster_general_namespaces(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/general/ingressClasses")
def get_general_ingress_classes(current_user: Annotated[UserSchema, Depends(admin_required)],cluster_id:int, db: Session = Depends(get_db)):
    return get_cluster_ingress_classes(current_user, cluster_id, db)

# Get k8s objects yaml object
@router.get("/cluster/{cluster_id}/yaml")
def get_object_yaml(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, kind:str, name:str, namespace:str, db: Session = Depends(get_db)):
    return get_object(current_user, ObjectSchema(kind=kind, name=name, namespace=namespace,cluster_id=cluster_id), db)

@router.put("/cluster/yaml")
def update_object_yaml(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], object: Json = Form(...), yaml_file: UploadFile = File(...), db: Session = Depends(get_db)):
    object = json.loads(json.dumps(object))
    return update_object(current_user,ObjectSchema(**object),yaml_file, db)

# Delete k8s objects from cluster
@router.delete("")
def delete_object_from_cluster(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], object: ObjectSchema, db: Session = Depends(get_db)):
    return delete_object(current_user, object, db)


@router.post("")
def add_object( current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], object: Json = Form(...), object_file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Getting project as json to make a workaround for common issue "value is not a valid dict" => src "https://github.com/tiangolo/fastapi/issues/5349"
    python_dict = json.loads(json.dumps(object))
    return add_object_to_cluster(current_user, object_file, ObjectAddSchema(**python_dict), db)

# Get default values yaml of the templates
@router.get("/templates/values")
def get_template_values(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], kind:Literal[
    'service',
    'ingress',
    'configmap',
    'secret'
]):
    return get_chart_values(kind)