from utils.provider import exist_provider, get_provider_infos
from fastapi import Depends, APIRouter
from database.postgres_db import get_db
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/{provider}/instance_types")
def get_instance_types(provider: str, db: Session = Depends(get_db)):
    if not exist_provider(provider):
        return JSONResponse(content = {"error": "provider does not exist", "i18n_code": "504"}, status_code = 404)
    return {
        "status": "ok",
        "types": get_provider_infos(provider, "instance_types")
    }
