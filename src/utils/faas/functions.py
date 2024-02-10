from utils.common import is_false, is_not_empty

_supported_languages = ["python", "go", "javascript", "bash"]

def is_supported_language (lng):
    return is_not_empty(lng) and any(c == "{}".format(lng).lower() for c in _supported_languages)

def is_not_supported_language(lng):
    return not is_supported_language(lng)

def is_not_owner(current_user, function):
    return current_user is None or (is_false(current_user.is_admin) and current_user.id != function.owner_id)

def get_ext_from_language(lng):
    if "go" == lng.lower():
        return "go"
    elif "javascript" == lng.lower():
        return "js"
    elif "bash" == lng.lower():
        return "sh"
    else:
        return "py"
