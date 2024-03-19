from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from database.postgres_db import get_db
from schemas.User import UserSchema
from middleware.auth_guard import get_current_active_user
from middleware.k8sapi_guard import k8sapi_required
from controllers.kubernetes.cluster import get_clusters_limited

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "k8s-cluster"
_counter = create_counter("k8s_cluster_api", "K8S cluster API counter")

@router.get("")
def get_clusters(current_user: Annotated[UserSchema, Depends(get_current_active_user)], k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return get_clusters_limited(current_user, db)
