from entities.User import User
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Annotated

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from controllers.faas.user import get_owner_email
from controllers.faas.functions import get_all_functions, get_function
from utils.common import is_false

router = APIRouter()

@router.get("/functions")
def find_all_functions(response: Response, current_user: Annotated[UserSchema, Depends(admin_required)], start_index: int = 0, max_results: int = 10, db: Session = Depends(get_db)):
    results = get_all_functions(db, current_user, start_index, max_results)
    response.status_code = results['code']
    return results

@router.get("/function/{id}/owner")
def find_owner_by_function_id(id: str, response: Response, current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    result = get_function(id, current_user, db)
    response.status_code = result['code']

    if is_false(result['status']):
        return result

    return {
        "username": get_owner_email(result['entity'], db),
        "id": result['entity'].owner_id
    }
