import os
import json

from schemas.Ai import PromptSchema
from utils.common import get_env_float, get_env_int, is_empty, is_not_empty, is_numeric, is_true
from utils.logger import log_msg

_default_models = [
    'gpt2',
    'nlptownsentiment',
    'nltksentiment',
    'textblobsentiment',
    'robertaemotion',
    'log'
]

CWAI_ENABLE = is_true(os.getenv("CWAI_ENABLE", "false"))
CWAI_LOW_CPU_MEM = is_true(os.getenv("CWAI_LOW_CPU_MEM", "true"))
CWAI_TOKENIZER_USE_FAST = is_true(os.getenv("CWAI_TOKENIZER_USE_FAST", "true"))
DEFAULT_MAX_LENGTH = get_env_int("DEFAULT_MAX_LENGTH", 50)
DEFAULT_NUM_RETURN_SEQUENCES =  get_env_int("DEFAULT_NUM_RETURN_SEQUENCES", 1) 
DEFAULT_NO_REPEAT_NGRAM_SIZE = get_env_int("DEFAULT_NO_REPEAT_NGRAM_SIZE", 2)
DEFAULT_TOP_K = get_env_int("DEFAULT_TOP_K", 50)
DEFAULT_TOP_P = get_env_float("DEFAULT_TOP_P", 0.95)
DEFAULT_TEMPERATURE = get_env_float("DEFAULT_TEMPERATURE", 0.8)

def get_max_length(prompt: PromptSchema):
    return prompt.settings.max_length if prompt.settings is not None and is_numeric(prompt.settings.max_length) else DEFAULT_MAX_LENGTH

def get_num_return_sequences(prompt: PromptSchema):
    return prompt.settings.num_return_sequences if prompt.settings is not None and is_numeric(prompt.settings.num_return_sequences) else DEFAULT_NUM_RETURN_SEQUENCES

def get_no_repeat_ngram_size(prompt: PromptSchema):
    return prompt.settings.no_repeat_ngram_size if prompt.settings is not None and is_numeric(prompt.settings.no_repeat_ngram_size) else DEFAULT_NO_REPEAT_NGRAM_SIZE

def get_top_k(prompt: PromptSchema):
    return prompt.settings.top_k if prompt.settings is not None and is_numeric(prompt.settings.top_k) else DEFAULT_TOP_K

def get_top_p(prompt: PromptSchema):
    return prompt.settings.top_p if prompt.settings is not None and is_not_empty(prompt.settings.top_p) else DEFAULT_TOP_P

def get_temperature(prompt: PromptSchema):
    return prompt.settings.temperature if prompt.settings is not None and is_not_empty(prompt.settings.temperature) else DEFAULT_TEMPERATURE

def get_all_models():
    models_json = os.getenv('CWAI_ENABLED_MODELS')
    if is_empty(models_json):
        return _default_models

    try:
        return json.loads(models_json)
    except Exception as e:
        log_msg("WARN", "[get_all_models] invalid list of models, loading the default list: e.type = {}, e.msg = {}".format(type(e), e))
        return _default_models

def get_first_model():
    return get_all_models()[0]
