import os
import requests
from requests.auth import HTTPBasicAuth
from middleware.cwaiapi_guard import cwaiapi_required
from utils.common import is_not_empty, is_response_ok
from utils.logger import log_msg
from fastapi import Depends, status, APIRouter
from typing import Annotated
from schemas.User import UserSchema
from schemas.Ai import PromptSchema
from middleware.auth_guard import get_current_active_user
from sqlalchemy.orm import Session
from database.postgres_db import get_db
from fastapi.responses import JSONResponse

CWAI_API_URL = os.getenv("CWAI_API_URL")
CWAI_API_USERNAME = os.getenv("CWAI_API_USERNAME")
CWAI_API_PASSWORD = os.getenv("CWAI_API_PASSWORD")

router = APIRouter()

@router.post("/prompt", status_code = status.HTTP_201_CREATED)
def create_prompt(current_user: Annotated[UserSchema, Depends(get_current_active_user)], cwai: Annotated[str, Depends(cwaiapi_required)], prompt: PromptSchema, db: Session = Depends(get_db)):
    endpoint = "{}/v{}/prompt/{}".format(CWAI_API_URL, 3 if "settings" in prompt and is_not_empty(prompt.settings) else 2, prompt.model)

    auth = HTTPBasicAuth(CWAI_API_USERNAME, CWAI_API_PASSWORD) if is_not_empty(CWAI_API_USERNAME) and is_not_empty(CWAI_API_PASSWORD) else None
    payload = prompt.dict()
    del payload['model']
    result = requests.post(endpoint, auth = auth, json = payload)
    log_msg("DEBUG", "[cwai][prompt] user = {}, response code = {}".format(current_user.email, result.status_code))
    if is_response_ok(result.status_code):
        return JSONResponse(content = result.json(), status_code = result.status_code)
    else:
        try:
            answer = result.json()
            answer["i18n_code"] = "cwai_error"
            if "response" in answer and len(answer["response"]) > 0 and "model not found" == answer["response"][0]:
                answer["i18n_code"] = "cwai_model_notfound"
        except Exception as e:
            response = "response = {}".format(result.content)
            log_msg("WARN", "[prompt] invalid json answer :{}".format(response))
            answer = { "status": "ko", "reason": response, "i18n_code": "cwai_error"}
        return JSONResponse(content = answer, status_code = result.status_code)
