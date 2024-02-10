from fastapi import APIRouter, Depends, Response
from typing import Annotated

from controllers.faas.languages import get_supported_languages
from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema

router = APIRouter()

@router.get("/languages")
def find_all_languages(response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)]):
    results = get_supported_languages()
    response.status_code = results['code']
    return results
