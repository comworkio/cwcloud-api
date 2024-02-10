from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Annotated

from middleware.faasapi_guard import faasapi_required
from middleware.auth_guard import admin_required
from database.postgres_db import get_db
from schemas.User import UserSchema
from schemas.faas.Trigger import Trigger, CompletedTrigger
from controllers.faas.triggers import add_trigger, clear_my_triggers, delete_trigger, get_my_triggers, get_trigger, override_trigger

from utils.common import is_false

router = APIRouter()

@router.post("/trigger")
def create_trigger(payload: Trigger, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    result = add_trigger(payload, current_user, db)
    response.status_code = result['code']
    return result

@router.put("/trigger/{id}")
def update_trigger(id: str, payload: CompletedTrigger, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    result = override_trigger(id, current_user, payload, db)
    response.status_code = result['code']
    return result

@router.get("/trigger/{id}")
def find_trigger_by_id(id: str, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    result = get_trigger(id, current_user, db)
    response.status_code = result['code']
    if is_false(result['status']):
        return result

    return result['entity']

@router.get("/triggers")
def find_my_triggers(response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], kind: str = None, start_index: int = 0, max_results: int = 10, db: Session = Depends(get_db)):
    results = get_my_triggers(db, current_user, kind, start_index, max_results)
    response.status_code = results['code']
    return results

@router.delete("/trigger/{id}")
def delete_trigger_by_id(id: str, response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    result = delete_trigger(id, current_user, db)
    response.status_code = result['code']
    return result

@router.delete("/triggers")
def delete_all_triggers(response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)], db: Session = Depends(get_db)):
    result = clear_my_triggers(current_user, db)
    response.status_code = result['code']
    return result
