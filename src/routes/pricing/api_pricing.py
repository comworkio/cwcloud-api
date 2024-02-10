from urllib.error import HTTPError
from utils.provider import get_provider_instances_pricing
from fastapi import Depends, APIRouter
from database.postgres_db import get_db
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse


router = APIRouter()
@router.get("/{provider}/pricing")
def get(provider: str, db: Session = Depends(get_db)):
    try:
        prices = get_provider_instances_pricing(provider)
        return {
        "status": "ok",
        "prices": prices
        }
    except HTTPError as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
