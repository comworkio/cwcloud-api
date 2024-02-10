import re

from utils.common import is_empty, is_not_empty

def marshall_list_string(roles):
    if is_empty(roles):
        return ""

    if not isinstance(roles, list):
        return roles

    all_roles = ""
    for role in roles:
        all_roles = "{};{}".format(all_roles, role)

    return all_roles[1:] if is_not_empty(all_roles) else all_roles

def unmarshall_list_array(roles_str):
    if is_not_empty(roles_str) and isinstance(roles_str, list):
        return roles_str

    return re.split(r"\,|\;", roles_str) if is_not_empty(roles_str) else []
