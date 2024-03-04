from database.postgres_db import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from typing import Annotated
from schemas.User import UserSchema
from middleware.auth_guard import get_current_active_user
from middleware.k8sapi_guard import k8sapi_required
from controllers.kubernetes.cluster import get_clusters_limited

router = APIRouter()

@router.get("")
def get_clusters(current_user: Annotated[UserSchema, Depends(get_current_active_user)], k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    return get_clusters_limited(current_user, db)