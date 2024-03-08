import json

from typing import Literal, Annotated
from pydantic import Json
from sqlalchemy.orm import Session
from fastapi import APIRouter, Form, UploadFile, File, Depends

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from middleware.k8sapi_guard import k8sapi_required
from schemas.Kubernetes import ObjectAddSchema, ObjectSchema
from schemas.User import UserSchema
from controllers.admin.admin_k8s_objects import add_object_to_cluster, delete_object, get_cluster_config_maps,get_object, get_cluster_services, get_cluster_ingresses ,update_object,get_chart_values,get_cluster_secrets,get_cluster_general_services,get_cluster_general_namespaces, get_cluster_ingress_classes

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-k8s-object"

@router.get("/cluster/{cluster_id}/services")
def get_services(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-svc".format(_span_prefix)):
        return get_cluster_services(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/configMaps")
def get_config_maps(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-cm".format(_span_prefix)):
        return get_cluster_config_maps(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/ingresses")
def get_ingresses(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
   with get_otel_tracer().start_as_current_span("{}-ingresses".format(_span_prefix)):
    return get_cluster_ingresses(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/secrets")
def get_secrets(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-secrets".format(_span_prefix)):
        return get_cluster_secrets(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/general/services")
def get_general_services(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-general-svc".format(_span_prefix)):
        return get_cluster_general_services(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/general/namespaces")
def get_general_namespaces(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-general-ns".format(_span_prefix)):
        return get_cluster_general_namespaces(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/general/ingressClasses")
def get_general_ingress_classes(current_user: Annotated[UserSchema, Depends(admin_required)],cluster_id:int, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-ingress-classes".format(_span_prefix)):
        return get_cluster_ingress_classes(current_user, cluster_id, db)

@router.get("/cluster/{cluster_id}/yaml")
def get_object_yaml(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], cluster_id:int, kind:str, name:str, namespace:str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return get_object(current_user, ObjectSchema(kind=kind, name=name, namespace=namespace,cluster_id=cluster_id), db)

@router.put("/cluster/yaml")
def update_object_yaml(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], object: Json = Form(...), yaml_file: UploadFile = File(...), db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-put".format(_span_prefix)):
        object = json.loads(json.dumps(object))
        return update_object(current_user,ObjectSchema(**object), yaml_file, db)

@router.delete("")
def delete_object_from_cluster(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], object: ObjectSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        return delete_object(current_user, object, db)

@router.post("")
def add_object( current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], object: Json = Form(...), object_file: UploadFile = File(...), db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        python_dict = json.loads(json.dumps(object))
        return add_object_to_cluster(current_user, object_file, ObjectAddSchema(**python_dict), db)

@router.get("/templates/values")
def get_template_values(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], kind:Literal[
    'service',
    'ingress',
    'configmap',
    'secret'
]):
    with get_otel_tracer().start_as_current_span("{}-templates".format(_span_prefix)):
        return get_chart_values(kind)
