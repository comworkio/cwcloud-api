from enum import Enum
from prometheus_client import Counter

from utils.common import sanitize_metric_name
from utils.observability.cid import get_current_cid
from utils.observability.enums import Action, Method, is_unknown
from utils.observability.otel import get_otel_meter

def create_counter(name, description):
    name = sanitize_metric_name(name)
    return {
        'otel': get_otel_meter().create_counter(
                    name = name,
                    description = description,
                    unit = "1"
                ),
        'prom': Counter(name, description, ['cid', 'method', 'action'])
    }

def increment_counter(counter, method: Enum = Method.UNKNOWN, action = Action.UNKNOWN):
    cid = get_current_cid()
    if is_unknown(action):
        action = method

    str_action = action.name.lower()
    str_method = method.name.lower()
    counter['otel'].add(1, {"cid": cid, "method": str_method, "action": str_action})
    counter['prom'].labels(cid, str_method, str_action).inc()
