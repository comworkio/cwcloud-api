from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from database.postgres_db import get_db
from schemas.User import UserSchema
from middleware.auth_guard import get_current_active_user
from middleware.k8sapi_guard import k8sapi_required
from controllers.kubernetes.cluster import get_clusters_limited

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "k8s-cluster"

@router.get("")
def get_clusters(current_user: Annotated[UserSchema, Depends(get_current_active_user)], k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return get_clusters_limited(current_user, db)
