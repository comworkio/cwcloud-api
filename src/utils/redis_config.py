import os

from utils.common import is_empty, is_not_numeric

def get_host_and_port(redis_url):
    if is_empty(redis_url):
        raise ValueError("The redis host is not set")

    try:
        host, port = redis_url.split(":")
    except ValueError as e:
        host = redis_url
        port = "6379"

    if is_not_numeric(port):
        raise ValueError("The redis port must be an integer value")

    return host, int(port)

def get_host_and_port_from_env():
    redis_url = os.getenv('REDIS_URL')
    if is_empty(redis_url):
        redis_url = os.getenv('REDIS_HOST')

    return get_host_and_port(redis_url)
