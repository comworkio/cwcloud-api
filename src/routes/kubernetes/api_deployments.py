from database.postgres_db import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends
from typing import Annotated
from schemas.User import UserSchema
from schemas.Kubernetes import DeploymentSchema
from middleware.auth_guard import get_current_user
from middleware.k8sapi_guard import k8sapi_required
from controllers.kubernetes.deployments import create_new_deployment,get_deployments, delete_deployment,get_deployment

router = APIRouter()

@router.post("")
def create_deployment(current_user: Annotated[UserSchema, Depends(get_current_user)], k8s: Annotated[str, Depends(k8sapi_required)], deployment:DeploymentSchema , db: Session = Depends(get_db)):
    return create_new_deployment(current_user,deployment,db)

@router.get("")
def get_all_deployments(current_user: Annotated[UserSchema, Depends(get_current_user)], k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    return get_deployments(current_user,db)

@router.get("/{deployment_id}")
def get_deployment_by_id(current_user: Annotated[UserSchema, Depends(get_current_user)], k8s: Annotated[str, Depends(k8sapi_required)], deployment_id:int, db: Session = Depends(get_db)):
    return get_deployment(current_user,deployment_id,db)

@router.delete("/{deployment_id}")
def delete_deployment_by_id(current_user: Annotated[UserSchema, Depends(get_current_user)], k8s: Annotated[str, Depends(k8sapi_required)], deployment_id:int, db: Session = Depends(get_db)):
    return delete_deployment(current_user,deployment_id,db)