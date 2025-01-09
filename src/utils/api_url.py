import os
from utils.common import get_env_int, is_empty
import requests
from urllib.parse import urlparse

from utils.http import HTTP_REQUEST_TIMEOUT

def get_api_url():
    api_url = os.getenv('API_URL')

    if is_empty(api_url):
        ENV = os.getenv('APP_ENV')
        if ENV == "local":
            return "http://localhost:5000"
        elif ENV == "prod":
            return "https://api.cwcloud"
        else:
            return "https://api.{}.cwcloud.tech".format(ENV)

    return api_url

def is_url_responding(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        return False

    try:
        response = requests.head(url, timeout=HTTP_REQUEST_TIMEOUT)
        return response.status_code < 400
    except requests.RequestException:
        return False

def is_url_not_responding(url):
    return not is_url_responding(url)
