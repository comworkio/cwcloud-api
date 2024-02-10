import re
import os

from jose import jwt

_JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def jwt_decode(token):
    return jwt.decode(re.sub("^[A-Za-z]+\ +", "", token), _JWT_SECRET_KEY)

def jwt_encode(data):
    return jwt.encode(data, _JWT_SECRET_KEY)
