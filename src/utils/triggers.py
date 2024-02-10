from utils.common import is_not_empty

_supported_triggers_kinds = ["cron"]

def is_supported_kind (kind):
    return is_not_empty(kind) and any(k == "{}".format(kind).lower() for k in _supported_triggers_kinds)

def is_not_supported_kind (kind):
    return not is_supported_kind(kind)
