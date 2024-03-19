from enum import Enum
from utils.observability.enums import Action, is_not_unknown

def span_format(prefix, method: Enum, action: Enum = Action.UNKNOWN):
    if is_not_unknown(action) and method.name != action.name:
        return "{}-{}-{}".format(prefix, method.name, action.name).lower()

    return "{}-{}".format(prefix, method.name).lower()
