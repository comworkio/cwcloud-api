from entities.User import User
from utils.common import is_empty, is_not_empty, is_true
from utils.security import is_not_email_valid

def override_owner_id(payload, old_data, current_user, db):
    if current_user.is_admin and is_not_empty(payload.owner_username):
        if is_not_email_valid(payload.owner_username):
            return {
                'status': 'ko',
                'code': 400,
                'error': "Owner email is not valid: {}".format(payload.owner_username),
                'i18n_code': 'not_valid_email'
            }

        db_owner = User.getUserByEmail(payload.owner_username, db)
        if not db_owner:
            return {
                'status': 'ko',
                'code': 404,
                'error': "User {} not found".format(payload.owner_username),
                'i18n_code': 'user_not_found'
            }

        return {
            'status': 'ok',
            'owner_id': db_owner.id
        }

    return {
        'status': 'ok',
        'owner_id': payload.owner_id if is_true(current_user.is_admin) and is_not_empty(payload.owner_id) else old_data.owner_id
    }

def get_owner_id(payload, current_user):
    return payload.owner_id if is_true(current_user.is_admin) and is_not_empty(payload.owner_id) else current_user.id


def get_email_owner(payload, db):
    if is_empty(payload.owner_id):
        return None

    user = User.getUserById(payload.owner_id, db)
    if not user:
        return None

    return user.email
