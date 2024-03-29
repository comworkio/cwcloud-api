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
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "adm-faas-invocation"
_counter = create_counter("adm_faas_invocation_api", "Admin invocation API counter")

@router.get("/invocations")
def find_all_invocations(response: Response, current_user: Annotated[UserSchema, Depends(admin_required)], start_index: int = 0, max_results: int = 10, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        results = get_all_invocations(db, current_user, start_index, max_results)
        response.status_code = results['code']
        return results

@router.get("/invocation/{id}/invoker")
def find_invoker_by_invocation_id(id: str, response: Response, current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.INVOKER)):
        increment_counter(_counter, Method.GET, Action.INVOKER)
        result = get_invocation(id, current_user, db)
        response.status_code = result['code']

        if is_false(result['status']):
            return result

        return {
            'status': 'ok',
            'username': get_invoker_email(result['entity'], db),
            'id': result['entity'].invoker_id
        }
