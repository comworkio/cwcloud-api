from adapters.AdapterConfig import get_adapter_by_name
from schemas.Ai import PromptSchema
from utils.common import is_empty
from utils.logger import log_msg
from utils.observability.cid import get_current_cid

def generate_prompt(prompt: PromptSchema):
    if is_empty(prompt.model):
        return {
            'status': 'ko',
            'response': ['model mandatory'],
            'i18n_code': 'cwai_model_mandatory',
            'cid': get_current_cid(),
            'http_status': 400,
            'score': None
        }

    try:
        Adapter = get_adapter_by_name("ai", prompt.model)
    except ModuleNotFoundError as e:
        log_msg("WARN", "[prompt] model {} seems not found: {}".format(prompt.model, e))
        return {
            'status': 'ko',
            'response': ['model not found'],
            'i18n_code': 'cwai_model_notfound',
            'cid': get_current_cid(),
            'http_status': 404,
            'score': None
        }

    response = Adapter().generate_response(prompt)

    return {
        'status': 'ok',
        'response': response['response'],
        'cid': get_current_cid(),
        'score': response['score'] if 'score' in response else None
    }
