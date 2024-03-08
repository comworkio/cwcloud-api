from fastapi import APIRouter, Depends, Response
from typing import Annotated

from controllers.faas.languages import get_supported_languages
from middleware.faasapi_guard import faasapi_required
from schemas.User import UserSchema

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "faas-language"

@router.get("/languages")
def find_all_languages(response: Response, current_user: Annotated[UserSchema, Depends(faasapi_required)]):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        results = get_supported_languages()
        response.status_code = results['code']
        return results
