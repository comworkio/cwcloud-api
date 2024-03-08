from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from database.postgres_db import get_db

from utils.provider import exist_provider, get_provider_infos
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "instance-types"

@router.get("/{provider}/instance_types")
def get_instance_types(provider: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        if not exist_provider(provider):
            return JSONResponse(content = {"error": "provider does not exist", "i18n_code": "504"}, status_code = 404)
        return {
            "status": "ok",
            "types": get_provider_infos(provider, "instance_types")
        }
