import os

from utils.api_url import get_api_url
from utils.common import get_env_int

FAAS_API_URL = os.getenv('FAAS_API_URL', get_api_url())
FAAS_API_TOKEN = os.getenv('FAAS_API_TOKEN', 'changeit')
FAAS_API_MAX_RESULTS = get_env_int('API_MAX_RESULTS', 100)
