import os
from utils.common import is_empty
import urllib.request

def get_api_url():
    api_url = os.getenv('API_URL')

    if is_empty(api_url):
        ENV = os.getenv('APP_ENV')
        if ENV == "local":
            return "http://localhost:5000"
        elif ENV == "prod":
            return "https://cloud-api.comwork.io"
        else:
            return "https://{}.cloud-api.comwork.io".format(ENV)

    return api_url

def is_url_responding(url):
    try:
        with urllib.request.urlopen(url):
            return True
    except urllib.error.URLError:
        return False

def is_url_not_responding(url):
    return not is_url_responding(url)
