from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Annotated

from database.postgres_db import get_db
from schemas.User import UserSchema
from middleware.auth_guard import admin_required
from controllers.faas.user import get_invoker_email
from controllers.faas.invocations import get_all_invocations, get_invocation

from utils.common import is_false
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-faas-invocation"

@router.get("/invocations")
def find_all_invocations(response: Response, current_user: Annotated[UserSchema, Depends(admin_required)], start_index: int = 0, max_results: int = 10, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        results = get_all_invocations(db, current_user, start_index, max_results)
        response.status_code = results['code']
        return results

@router.get("/invocation/{id}/invoker")
def find_invoker_by_invocation_id(id: str, response: Response, current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-invoker".format(_span_prefix)):
        result = get_invocation(id, current_user, db)
        response.status_code = result['code']

        if is_false(result['status']):
            return result

        return {
            "username": get_invoker_email(result['entity'], db),
            "id": result['entity'].invoker_id
        }
