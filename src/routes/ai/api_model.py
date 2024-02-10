import os
import requests
from requests.auth import HTTPBasicAuth
from utils.common import is_not_empty
from utils.logger import log_msg
from fastapi import Depends, APIRouter
from database.postgres_db import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from schemas.User import UserSchema
from middleware.auth_guard import get_current_active_user
from middleware.cwaiapi_guard import cwaiapi_required
from fastapi.responses import JSONResponse

router = APIRouter()

CWAI_API_URL = os.getenv("CWAI_API_URL")
CWAI_API_USERNAME = os.getenv("CWAI_API_USERNAME")
CWAI_API_PASSWORD = os.getenv("CWAI_API_PASSWORD")

@router.get("/models")
def get_model(current_user: Annotated[UserSchema, Depends(get_current_active_user)], cwai: Annotated[str, Depends(cwaiapi_required)], db: Session = Depends(get_db)):
    endpoint = "{}/v1/models".format(CWAI_API_URL)
    auth = HTTPBasicAuth(CWAI_API_USERNAME, CWAI_API_PASSWORD) if is_not_empty(CWAI_API_USERNAME) and is_not_empty(CWAI_API_PASSWORD) else None
    result = requests.get(endpoint, auth = auth)
    log_msg("DEBUG", "[cwai][models] user = {}, response code = {}".format(current_user.email, result.status_code))
    return JSONResponse(content = result.json(), status_code = result.status_code)
