from fastapi import Depends

from schemas.User import UserSchema
from middleware.faasapi_guard import faasapi_required

from utils.faas.functions import _supported_languages

def get_supported_languages(current_user: UserSchema = Depends(faasapi_required)):
    return {
        'status': 'ok',
        'code': 200,
        'languages': _supported_languages
    }
