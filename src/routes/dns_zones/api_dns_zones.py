from utils.dns_zones import get_dns_zones
from fastapi import Depends, status, APIRouter
from database.postgres_db import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from schemas.User import UserSchema
from middleware.auth_guard import get_current_active_user

router = APIRouter()

@router.get("", status_code = status.HTTP_200_OK)
def get_all_dns_zones(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "zones": get_dns_zones()
    }
