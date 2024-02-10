from fastapi import APIRouter, Depends, Response
from typing import Annotated

from controllers.faas.trigger_kinds import get_all_triggers_kinds

from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema

router = APIRouter()

@router.get("/trigger_kinds")
def get_all_kinds(response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)]):
    results = get_all_triggers_kinds()
    response.status_code = results['code']
    return results
