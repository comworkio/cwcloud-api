import os

from utils.common import is_empty, is_not_empty

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
