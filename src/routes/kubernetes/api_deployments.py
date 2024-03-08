
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends

from database.postgres_db import get_db
from middleware.auth_guard import get_current_user
from middleware.k8sapi_guard import k8sapi_required
from schemas.User import UserSchema
from schemas.Kubernetes import DeploymentSchema
from controllers.kubernetes.deployments import create_new_deployment,get_deployments, delete_deployment,get_deployment

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "k8s-deployment"

@router.post("")
def create_deployment(current_user: Annotated[UserSchema, Depends(get_current_user)], k8s: Annotated[str, Depends(k8sapi_required)], deployment:DeploymentSchema , db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        return create_new_deployment(current_user, deployment, db)

@router.get("")
def get_all_deployments(current_user: Annotated[UserSchema, Depends(get_current_user)], k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return get_deployments(current_user, db)

@router.get("/{deployment_id}")
def get_deployment_by_id(current_user: Annotated[UserSchema, Depends(get_current_user)], k8s: Annotated[str, Depends(k8sapi_required)], deployment_id:int, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return get_deployment(current_user, deployment_id, db)

@router.delete("/{deployment_id}")
def delete_deployment_by_id(current_user: Annotated[UserSchema, Depends(get_current_user)], k8s: Annotated[str, Depends(k8sapi_required)], deployment_id:int, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        return delete_deployment(current_user, deployment_id, db)
