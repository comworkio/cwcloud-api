from adapters.AdapterConfig import get_adapter_by_name

from utils.logger import log_msg
from utils.observability.cid import get_current_cid

def async_load(model: str):
    try:
        adapter = get_adapter_by_name("ai", model)
        adapter().load_model()
    except ModuleNotFoundError as e:
        log_msg("WARN", "[model] model {} seems not found: {}".format(model, e))

def load(model: str, bt):
    bt.add_task(async_load, model)
    return {
        'status': 'ok',
        'http_status': 202
    }
