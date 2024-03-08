from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database.postgres_db import get_db

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "ping"

@router.get("")
def get_ping(db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return {
            "status": "ok",
            "alive": True
        }
