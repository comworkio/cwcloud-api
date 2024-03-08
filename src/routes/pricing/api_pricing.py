from urllib.error import HTTPError
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from database.postgres_db import get_db

from utils.observability.otel import get_otel_tracer
from utils.provider import get_provider_instances_pricing

router = APIRouter()

_span_prefix = "pricing"

@router.get("/{provider}/pricing")
def get(provider: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        try:
            prices = get_provider_instances_pricing(provider)
            return {
                "status": "ok",
                "prices": prices
            }
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
