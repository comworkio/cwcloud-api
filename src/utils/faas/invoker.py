from entities.User import User
from utils.common import is_empty, is_not_empty, is_true
from utils.security import is_not_email_valid

def override_invoker_id(payload, old_data, current_user, db):
    if current_user.is_admin and is_not_empty(payload.invoker_username):
        if is_not_email_valid(payload.invoker_username):
            return {
                'status': 'ko',
                'code': 400,
                'error': "Owner email is not valid: {}".format(payload.invoker_username),
                'i18n_code': 'not_valid_email'
            }

        db_owner = User.getUserByEmail(payload.invoker_username, db)
        if not db_owner:
            return {
                'status': 'ko',
                'code': 404,
                'error': "User {} not found".format(payload.invoker_username),
                'i18n_code': 'user_not_found'
            }

        return {
            'status': 'ok',
            'invoker_id': db_owner.id
        }

    return {
        'status': 'ok',
        'invoker_id': payload.invoker_id if is_true(current_user.is_admin) and is_not_empty(payload.invoker_id) else old_data.invoker_id
    }

def get_invoker_id(payload, current_user):
    if is_empty(current_user):
        return None

    return payload.invoker_id if is_true(current_user.is_admin) and is_not_empty(payload.invoker_id) else current_user.id

def get_email_invoker(payload, db):
    if is_empty(payload.invoker_id):
        return None

    user = User.getUserById(payload.invoker_id, db)
    if not user:
        return None

    return user.email
