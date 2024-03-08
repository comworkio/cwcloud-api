
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, UploadFile, File, Depends

from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from middleware.k8sapi_guard import k8sapi_required
from schemas.User import UserSchema
from controllers.admin.admin_k8s_cluster import get_all_clusters, get_cluster_infos, get_clusters_byKubeconfigFile, save_kubeconfig, delete_cluster_by_id

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-k8s-cluster"

@router.post("")
def upload_kubeconfig( current_user: Annotated[UserSchema, Depends(get_current_active_user)], k8s: Annotated[str, Depends(k8sapi_required)], kubeconfig: UploadFile = File(...), db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        return save_kubeconfig(current_user, kubeconfig, db)

@router.get("")
def get_clusters(current_user: Annotated[UserSchema, Depends(get_current_active_user)], k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return get_all_clusters(db)

@router.get("/{kube_id}")
def get_clusters_by_kubeconfig(current_user: Annotated[UserSchema, Depends(get_current_active_user)],kube_id:int, k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        return get_clusters_byKubeconfigFile(current_user, kube_id, db)

@router.get("/{cluster_id}/info")
def get_cluster_info(current_user: Annotated[UserSchema, Depends(get_current_active_user)],cluster_id: int, k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-info".format(_span_prefix)):
        return get_cluster_infos(current_user, cluster_id, db)

@router.delete("/{cluster_id}")
def delete_cluster(current_user: Annotated[UserSchema, Depends(get_current_active_user)], cluster_id:int, k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        return delete_cluster_by_id(current_user, cluster_id, db)
