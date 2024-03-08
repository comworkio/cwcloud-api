from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Annotated

from database.postgres_db import get_db
from middleware.auth_guard import get_current_not_mandatory_user, get_current_user, get_user_authentication
from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema
from schemas.faas.Invocation import Invocation, CompletedInvocation
from schemas.UserAuthentication import UserAuthentication
from controllers.faas.invocations import clear_my_invocations, invoke, invoke_sync, complete, get_invocation, get_my_invocations, delete_invocation

from utils.common import is_not_empty_key, is_true
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "faas-invocation"

@router.post("/invocation")
def create_invocation(payload: Invocation, response: Response, current_user: Annotated[UserSchema, Depends(get_current_not_mandatory_user)], user_auth: Annotated[UserAuthentication, Depends(get_user_authentication)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        result = invoke(payload, current_user, user_auth, db)
        response.status_code = result['code']
        return result

@router.post("/invocation/sync")
def create_sync_invocation(payload: Invocation, response: Response, current_user: Annotated[UserSchema, Depends(get_current_not_mandatory_user)], user_auth: Annotated[UserAuthentication, Depends(get_user_authentication)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post-sync".format(_span_prefix)):
        result = invoke_sync(payload, current_user, user_auth, db)
        response.status_code = result['code']
        return result

@router.put("/invocation/{id}")
def update_invocation(id: str, payload: CompletedInvocation, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-put".format(_span_prefix)):
        result = complete(id, payload, current_user, db)
        response.status_code = result['code']
        return result

@router.get("/invocation/{id}")
def find_invocation_by_id(id: str, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        result = get_invocation(id, current_user, db)
        response.status_code = result['code']
        return result['entity'] if is_true(result['status']) and is_not_empty_key(result, 'entity') else result

@router.get("/invocations")
def find_my_invocations(response: Response, current_user: Annotated[UserSchema, Depends(get_current_user)], start_index: int = 0, max_results: int = 10, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        results = get_my_invocations(db, current_user, start_index, max_results)
        response.status_code = results['code']
        return results

@router.delete("/invocation/{id}")
def delete_invocation_by_id(id: str, response: Response, current_user: Annotated[UserSchema, Depends(get_current_user)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        result = delete_invocation(id, current_user, db)
        response.status_code = result['code']
        return result

@router.delete("/invocations")
def delete_all_invocations(response: Response, current_user: Annotated[UserSchema, Depends(get_current_user)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete-all".format(_span_prefix)):
        result = clear_my_invocations(current_user, db)
        response.status_code = result['code']
        return result

