from utils.common import is_false, is_not_empty, is_not_empty_key

_supported_languages = ["python", "go", "javascript", "bash"]
_supported_callback_types = ["http", "websocket", "mqtt"]

def is_supported_language(lng):
    return is_not_empty(lng) and any(c == "{}".format(lng).lower() for c in _supported_languages)

def is_not_supported_language(lng):
    return not is_supported_language(lng)

def is_supported_callback_type(tp):
    return is_not_empty(tp) and any(c == "{}".format(tp).lower() for c in _supported_callback_types)

def is_not_supported_callback_type(tp):
    return not is_supported_callback_type(tp)

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
    
#? this function is for legacy faas functions to restructure their content's callbacks
def restructure_callbacks(content):
    if "callback_url" in content and "callback_authorization_header" in content:
        callback = {
            "endpoint": content.pop("callback_url"),
            "token": content.pop("callback_authorization_header"),
            "type": "http"
        }
        content["callbacks"] = [callback]
    
    return content

