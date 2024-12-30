from adapters.AdapterConfig import get_adapter_by_name

from utils.ai.default_values import get_all_models
from utils.common import is_empty
from utils.logger import log_msg
from utils.observability.cid import get_current_cid

def async_load(model: str):
    try:
        adapter = get_adapter_by_name("ai", model)
        adapter().load_model()
    except ModuleNotFoundError as e:
        log_msg("WARN", "[model][async_load] model {} seems not found: {}".format(model, e))

def load(model: str, bt):
    if is_empty(model):
        return {
            'status': 'ko',
            'i18n_code': 'cwai_model_mandatory',
            'cid': get_current_cid(),
            'http_status': 400
        }

    if model not in get_all_models():
        log_msg("WARN", "[model][load] model {} not found".format(model))
        return {
            'status': 'ko',
            'i18n_code': 'cwai_model_notfound',
            'cid': get_current_cid(),
            'http_status': 404
        }

    bt.add_task(async_load, model)
    return {
        'status': 'ok',
        'http_status': 202
    }
