from jose import JWTError

from sqlalchemy.orm import Session
from fastapi import Depends, status, APIRouter, Header
from fastapi.security import APIKeyHeader

from schemas.Token import TokenData
from schemas.User import UserSchema
from schemas.UserAuthentication import UserAuthentication
from entities.User import User
from entities.Apikeys import ApiKeys
from exceptions.CwHTTPException import CwHTTPException
from database.postgres_db import get_db
from adapters.AdapterConfig import get_adapter

from utils.common import is_empty, is_not_empty, is_false
from utils.jwt import jwt_decode
from utils.logger import log_msg

router = APIRouter()
CACHE_ADAPTER = get_adapter('cache')

def is_mock_test():
    return False

def get_mock_current_user():
    return None

user_token_header = APIKeyHeader(name = "X-User-Token", auto_error = False)

async def get_mem_user_token(user_token):
    decoded_user = jwt_decode(user_token)
    email: str = decoded_user.get("email")
    log_msg("DEBUG", "[auth_guard][get_mem_user_token] decoded_user = {}".format(decoded_user))
    return CACHE_ADAPTER().get(email), TokenData(email = email)

async def get_user_authentication(user_token: str = Depends(user_token_header), X_Auth_Token: str = Header(None, include_in_schema = False)):
    if is_not_empty(user_token):
        user_auth = UserAuthentication(is_authenticated = True, header_key = "X-User-Token", header_value = user_token)
        return { "is_authenticated": True, "header_key": "X-User-Token", "header_value": user_token }
    elif is_not_empty(X_Auth_Token):
        user_auth = UserAuthentication(is_authenticated = True, header_key = "X-Auth-Token", header_value = X_Auth_Token)
    else:
        user_auth = UserAuthentication(is_authenticated = False)
    return user_auth

async def get_current_not_mandatory_user(user_token: str = Depends(user_token_header), X_Auth_Token: str = Header(None, include_in_schema = False), db: Session = Depends(get_db)):
        user = None
        if is_mock_test():
            current_user = get_mock_current_user()
            return current_user
        if is_not_empty(user_token):
            try:
                decoded_mem_token, token_data = await get_mem_user_token(user_token)
                if not decoded_mem_token:
                    log_msg("DEBUG", "[auth_guard][get_current_not_mandatory_user] mem_user_token is not defined")
                    return None
                if decoded_mem_token != user_token:
                    log_msg("DEBUG", "[auth_guard][get_current_not_mandatory_user] decoded_mem_token != user_token")
                    return None
                user = User.getUserByEmail(token_data.email, db)
            except JWTError as e:
                log_msg("DEBUG", "[auth_guard][get_current_not_mandatory_user] e.type = {}, e.msg = {}".format(type(e), e))
                return None
        else:
            if is_not_empty(X_Auth_Token):
                secret_key = X_Auth_Token
                user_api_key = ApiKeys.getApiKeyBySecretKey(secret_key, db)
                if is_empty(user_api_key):
                    log_msg("DEBUG", "[auth_guard][get_current_not_mandatory_user] user_api_key is not set")
                    return None

                user = User.getUserById(user_api_key.user_id, db)
            else:
                log_msg("DEBUG", "[auth_guard][get_current_not_mandatory_user] auth_token is not set")
                return None

        if is_empty(user):
            log_msg("DEBUG", "[auth_guard][get_current_not_mandatory_user] user is not found")
            return None

        return user

async def get_current_user(user_token: str = Depends(user_token_header), X_Auth_Token: str = Header(None, include_in_schema = False), db: Session = Depends(get_db)):
        user = None
        if is_mock_test():
            current_user = get_mock_current_user()
            return current_user
        if is_not_empty(user_token):
            try:
                decoded_mem_token, token_data = await get_mem_user_token(user_token)
                if not decoded_mem_token:
                    raise CwHTTPException(message = {"error": "authentification failed", "i18n_code": "auth_failed"}, status_code = status.HTTP_401_UNAUTHORIZED)
                if decoded_mem_token != user_token:
                    raise CwHTTPException(message = {"error": "authentification failed 2", "i18n_code": "auth_failed"}, status_code = status.HTTP_401_UNAUTHORIZED)

                user = User.getUserByEmail(token_data.email, db)
            except JWTError as e:
                raise CwHTTPException(message = {"error": "authentification failed", "i18n_code": "auth_failed"}, status_code = status.HTTP_401_UNAUTHORIZED)
        else:
            if is_not_empty(X_Auth_Token):
                secret_key = X_Auth_Token
                user_api_key = ApiKeys.getApiKeyBySecretKey(secret_key, db)
                if is_empty(user_api_key):
                    raise CwHTTPException(message = {"error": "authentification failed", "i18n_code": "auth_failed"}, status_code = status.HTTP_401_UNAUTHORIZED)
                user = User.getUserById(user_api_key.user_id, db)
            else:
                raise CwHTTPException(message = {"error": "authentification failed", "i18n_code": "auth_failed"}, status_code = status.HTTP_401_UNAUTHORIZED)
        if is_empty(user):
            raise CwHTTPException(message = {"error": "authentification failed", "i18n_code": "auth_failed"}, status_code = status.HTTP_401_UNAUTHORIZED)

        return user

async def get_current_active_user(current_user: UserSchema = Depends(get_current_user)):
    if is_false(current_user.confirmed):
        raise CwHTTPException(message = {"error": "your account has not been confirmed yet", "i18n_code": "account_not_confirmed"}, status_code = status.HTTP_403_FORBIDDEN)
    return current_user

async def admin_required(current_user: UserSchema = Depends(get_current_active_user)):
    if is_false(current_user.is_admin):
        raise CwHTTPException(message = {"error": "permission denied", "i18n_code": "permission_denied"}, status_code = status.HTTP_403_FORBIDDEN)
    return current_user
