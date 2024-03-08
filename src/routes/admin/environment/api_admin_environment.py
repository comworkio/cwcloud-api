from typing import Annotated, Literal
from fastapi import Depends, APIRouter, File, UploadFile
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from schemas.Environment import EnvironmentSchema, K8SEnvironmentSchema
from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from middleware.k8sapi_guard import k8sapi_required
from controllers.admin.admin_environment import admin_add_environment, admin_get_environment, admin_get_environments, admin_get_roles, admin_remove_environment, admin_update_environment, admin_export_environment, admin_import_environment, get_charts, admin_get_k8s_environment, admin_update_k8s_environment, admin_add_k8s_environment, admin_delete_k8s_environment

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-env"
_span_k8s_prefix = "{}-k8s".format(_span_prefix)

@router.get("/roles")
def get_roles(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-roles".format(_span_prefix)):
        return admin_get_roles(current_user)

@router.get("/all")
def get_all_environments(current_user: Annotated[UserSchema, Depends(admin_required)], type: Literal['vm','k8s'] = "vm", db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return admin_get_environments(type, db)

@router.get("/{environment_id}/export")
def export_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environment_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-export".format(_span_prefix)):
        return admin_export_environment(current_user, environment_id, db)

@router.get("/{environment_id}")
def get_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environment_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return admin_get_environment(environment_id, db)

@router.put("/{environment_id}")
def update_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environment_id: str, payload: EnvironmentSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-put".format(_span_prefix)):
        return admin_update_environment(environment_id, payload, db)

@router.delete("/{environment_id}")
def delete_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environment_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        return admin_remove_environment(environment_id, db)

@router.post("/import")
def import_environment(current_user: Annotated[UserSchema, Depends(admin_required)], env: UploadFile = File(...), db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-import".format(_span_prefix)):
        return admin_import_environment(env, db)

@router.post("")
def add_environment(current_user: Annotated[UserSchema, Depends(admin_required)], payload: EnvironmentSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        return admin_add_environment(payload, db)

@router.post("/kubernetes")
def create_k8s_environment(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], payload: K8SEnvironmentSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_k8s_prefix)):
        return admin_add_k8s_environment(payload, db)

@router.get("/kubernetes/charts")
def get_available_charts(current_user: Annotated[UserSchema, Depends(admin_required)], k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-charts".format(_span_k8s_prefix)):
        return get_charts()

@router.get("/kubernetes/{environment_id}")
def get_k8s_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environment_id: str, k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_k8s_prefix)):
        return admin_get_k8s_environment(environment_id, db)

@router.delete("/kubernetes/{environment_id}")
def delete_k8s_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environment_id: str,  k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_k8s_prefix)):
        return admin_delete_k8s_environment(environment_id, db)

@router.put("/kubernetes/{environment_id}")
def update_k8s_environment_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], environment_id: str, payload: K8SEnvironmentSchema, k8s: Annotated[str, Depends(k8sapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-put".format(_span_k8s_prefix)):
        return admin_update_k8s_environment(environment_id, payload, db)
