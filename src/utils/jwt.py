import re
import os

from jose import jwt

_jwt_secret_key = os.getenv("JWT_SECRET_KEY")

def jwt_decode(token):
    return jwt.decode(re.sub("^[A-Za-z]+\ +", "", token), _jwt_secret_key)

def jwt_encode(data):
    return jwt.encode(data, _jwt_secret_key)
