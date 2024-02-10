from utils.common import is_true

def has_write_right(current_user, object):
    return is_true(current_user.is_admin) or current_user.id == object.owner_id

def has_not_write_right(current_user, object):
    return not has_write_right(current_user, object)

def has_exec_right(current_user, function):
    return function.is_public or is_true(current_user.is_admin) or current_user.id == function.owner_id

def has_not_exec_right(current_user, function):
    return not has_exec_right(current_user, function)
