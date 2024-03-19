from fastapi import APIRouter, Depends, Response, File, UploadFile
from sqlalchemy.orm import Session
from typing import Annotated

from database.postgres_db import get_db
from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema
from controllers.faas.functions import get_my_functions, get_function, add_function, override_function, delete_function, export_function, import_new_function
from schemas.faas.Function import BaseFunction, Function

from utils.common import is_false
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "faas-function"
_counter = create_counter("faas_function_api", "FaaS function API counter")

@router.post("/function")
def create_function(payload: BaseFunction, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        result = add_function(payload, current_user, db)
        response.status_code = result['code']
        return result

@router.post("/function/import")
def import_function(current_user: Annotated[UserSchema, Depends(faasapi_required)], function_file: UploadFile = File(...), db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST, Action.IMPORT)):
        increment_counter(_counter, Method.POST, Action.IMPORT)
        return import_new_function(current_user, function_file, db)

@router.get("/functions")
def find_my_functions(response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], start_index: int = 0, max_results: int = 10, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        results = get_my_functions(db, current_user, start_index, max_results)
        response.status_code = results['code']
        return results

@router.put("/function/{id}")
def update_function(id: str, payload: Function, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.PUT)):
        increment_counter(_counter, Method.PUT)
        result = override_function(id, payload, current_user, db)
        response.status_code = result['code']
        return result

@router.get("/function/{id}")
def find_function_by_id(id: str, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        result = get_function(id, current_user, db)
        response.status_code = result['code']
        if is_false(result['status']):
            return result

        return result['entity']

@router.get("/function/{id}/export")
def export_function_by_id(current_user: Annotated[UserSchema, Depends(faasapi_required)], id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.EXPORT)):
        increment_counter(_counter, Method.GET, Action.EXPORT)
        return export_function(id, db)

@router.delete("/function/{id}")
def delete_function_by_id(id: str, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        result = delete_function(id, current_user, db)
        response.status_code = result['code']
        return result
