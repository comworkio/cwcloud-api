from entities.User import User

from utils.common import is_empty, is_false, is_not_numeric
from utils.observability.cid import get_current_cid

def user_from_body(body, db):
    user_id = body.user_id
    if is_not_numeric(user_id):
        email = body.email
        if is_empty(email):
            return {
                'status': 'ko',
                'message': 'The user_id or email is mandatory',
                'i18n_code': 'user_id_or_email_mandatory',
                'http_code': 400,
                'cid': get_current_cid()
            }

        return User.getUserByEmail(email, db)
    else:
        return User.getUserById(int(user_id), db)


def pick_user_id_if_exists(user):
    if is_false(user):
        return {
            'status': 'ko',
            'message': 'The user is not found',
            'i18n_code': 'user_not_found',
            'http_code': 404,
            'cid': get_current_cid()
        }
    elif user is dict:
        return user

    return {
        'status': 'ok',
        'id': user.id
    }

def user_id_from_body(body, db):
    return pick_user_id_if_exists(user_from_body(body, db))
