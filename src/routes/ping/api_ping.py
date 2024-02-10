from fastapi import Depends, APIRouter
from database.postgres_db import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("")
def get_ping(db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "alive": True
    }
