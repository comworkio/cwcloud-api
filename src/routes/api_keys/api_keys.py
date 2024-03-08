import json

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from schemas.User import UserSchema
from schemas.API_keys import ApiKeysSchema, ApiKeysVerificationSchema
from entities.Apikeys import ApiKeys

from utils.api_keys import generate_apikey_access_key, generate_apikey_secret_key
from utils.common import is_empty
from utils.encoder import AlchemyEncoder
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "api-keys"

@router.post("")
def create_api_key(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: ApiKeysSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        name = payload.name
        if is_empty(name):
            return JSONResponse(content = {"error": "please provide a name for the api key", "i18n_code": "invalid_api_key" }, status_code = 400)

        found = True
        generated_access_key = ""
        while found:
            generated_access_key = generate_apikey_access_key()
            from entities.Apikeys import ApiKeys
            users_with_access_key = ApiKeys.getApiKeysByAccessKey(generated_access_key, db)
            if len(users_with_access_key) == 0:
                found = False
        generated_secret_key = ""
        found = True
        while found:
            generated_secret_key = generate_apikey_secret_key()
            from entities.Apikeys import ApiKeys
            users_with_secret_key = ApiKeys.getApiKeysBySecretKey(generated_access_key, db)
            if len(users_with_secret_key) == 0:
                found = False
        api_key = ApiKeys(**payload.dict())
        api_key.access_key = generated_access_key
        api_key.secret_key = generated_secret_key
        api_key.user_id = current_user.id
        api_key.save(db)
        api_key_json = json.loads(json.dumps(api_key, cls = AlchemyEncoder))
        api_key_json["id"] = api_key.id
        return JSONResponse(content = api_key_json, status_code = 201)

@router.get("")
def get_api_keys(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        from entities.Apikeys import ApiKeys
        api_keys = ApiKeys.getUserApiKeys(current_user.id, db)
        keys = [{"id": key.id, "name": key.name, "created_at": key.created_at} for key in api_keys]
        return JSONResponse(content = {"api_keys": keys}, status_code = 200)

@router.delete("/{key_id}")
def delete_api_key(current_user: Annotated[UserSchema, Depends(get_current_active_user)], key_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        from entities.Apikeys import ApiKeys
        apiKey = ApiKeys.getUserApiKey(current_user.id, key_id, db)
        if not apiKey:
            return JSONResponse(content = {"error": "api key not found", "i18n_code": "0000000"}, status_code = 404)
        ApiKeys.deleteUserApiKey(current_user.id, key_id, db)
        return JSONResponse(content = {"message": "api key successfully deleted", "i18n_code": "0000000"}, status_code = 200)

@router.post("/verify")
def verify_api_key(payload: ApiKeysVerificationSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-verify".format(_span_prefix)):
        access_key = payload.access_key
        secret_key = payload.secret_key

        if is_empty(access_key):
            return JSONResponse(content = {"error": "please provide an access key", "i18n_code": "0000000"}, status_code = 400)

        if is_empty(secret_key):
            return JSONResponse(content = {"error": "please provide a secret key", "i18n_code": "0000000"}, status_code = 400)

        api_key = ApiKeys.getApiKey(access_key, secret_key, db)
        if is_empty(api_key):
            return JSONResponse(content = {"error": "invalid api key credentials"}, status_code = 401)
        return JSONResponse(content = {"message": "api key credentials are valid"}, status_code = 200)
